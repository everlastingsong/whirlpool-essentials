import asyncio
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from spl.token.constants import TOKEN_2022_PROGRAM_ID

from orca_whirlpool.context import WhirlpoolContext
from orca_whirlpool.utils import DecimalUtil, PriceMath, PDAUtil, TokenUtil, TickUtil, TickArrayUtil, PoolUtil
from orca_whirlpool.types import Percentage
from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID
from orca_whirlpool.instruction import WhirlpoolIx, DecreaseLiquidityParams, CollectFeesParams, CollectRewardParams, ClosePositionWithTokenExtensionsParams
from orca_whirlpool.transaction import TransactionBuilder
from orca_whirlpool.quote import QuoteBuilder, DecreaseLiquidityQuoteParams


load_dotenv()
RPC_ENDPOINT_URL = os.getenv("RPC_ENDPOINT_URL")
POSITION_PUBKEY = Pubkey.from_string("6acPePn5gAJz4SD9jNWqJKGvfo4oAT7cGUshtBqeEDTg")


async def main():
    # read wallet
    # - how to create: solana-keygen new -o wallet.json
    # - need some USDC and SAMO
    with Path("wallet.json").open() as f:
        keypair = Keypair.from_bytes(bytes(json.load(f)))
    print("wallet pubkey", keypair.pubkey())

    # create client
    connection = AsyncClient(RPC_ENDPOINT_URL)
    ctx = WhirlpoolContext(ORCA_WHIRLPOOL_PROGRAM_ID, connection, keypair)

    position_pubkey = POSITION_PUBKEY
    print("position pubkey", str(position_pubkey))

    # get position
    position = await ctx.fetcher.get_position(position_pubkey)
    whirlpool = await ctx.fetcher.get_whirlpool(position.whirlpool)
    token_a_decimal = (await ctx.fetcher.get_token_mint(whirlpool.token_mint_a)).decimals
    token_b_decimal = (await ctx.fetcher.get_token_mint(whirlpool.token_mint_b)).decimals
    print("whirlpool token_mint_a", whirlpool.token_mint_a)
    print("whirlpool token_mint_b", whirlpool.token_mint_b)
    print("whirlpool tick_spacing", whirlpool.tick_spacing)
    print("whirlpool tick_current_index", whirlpool.tick_current_index)
    print("whirlpool sqrt_price", whirlpool.sqrt_price)
    price = PriceMath.sqrt_price_x64_to_price(whirlpool.sqrt_price, token_a_decimal, token_b_decimal)
    print("whirlpool price", DecimalUtil.to_fixed(price, token_b_decimal))

    ta_lower_start_index = TickUtil.get_start_tick_index(position.tick_lower_index, whirlpool.tick_spacing)
    ta_upper_start_index = TickUtil.get_start_tick_index(position.tick_upper_index, whirlpool.tick_spacing)
    ta_lower_pubkey = PDAUtil.get_tick_array(ctx.program_id, position.whirlpool, ta_lower_start_index).pubkey
    ta_upper_pubkey = PDAUtil.get_tick_array(ctx.program_id, position.whirlpool, ta_upper_start_index).pubkey

    # position token account (Token-2022 program)
    position_ata = TokenUtil.derive_ata(ctx.wallet.pubkey(), position.position_mint, TOKEN_2022_PROGRAM_ID)

    tx = TransactionBuilder(ctx.connection, ctx.wallet)

    # create token accounts to receive fees and rewards
    mint_to_be_collected = [
        str(whirlpool.token_mint_a),
        str(whirlpool.token_mint_b),
    ]
    for ri in whirlpool.reward_infos:
        if PoolUtil.is_reward_initialized(ri):
            mint_to_be_collected.append(str(ri.mint))
    # dedup
    mint_to_be_collected = list(set(mint_to_be_collected))
    # derive ATA(or temporary WSOL address) and instructions
    token_account_map = {}
    for mint in mint_to_be_collected:
        key_with_ix = await TokenUtil.resolve_or_create_ata(ctx.connection, ctx.wallet.pubkey(), Pubkey.from_string(mint))
        tx.add_instruction(key_with_ix.instruction)
        token_account_map[mint] = key_with_ix.pubkey

    # decrease liquidity
    # note: decrease liquidity has same effect of update fees and rewards, so we can omit update_fees_and_rewards ix
    if position.liquidity > 0:
        # get quote
        acceptable_slippage = Percentage.from_fraction(1, 100)
        quote = QuoteBuilder.decrease_liquidity_by_liquidity(DecreaseLiquidityQuoteParams(
            liquidity=position.liquidity,
            sqrt_price=whirlpool.sqrt_price,
            tick_current_index=whirlpool.tick_current_index,
            tick_upper_index=position.tick_upper_index,
            tick_lower_index=position.tick_lower_index,
            slippage_tolerance=acceptable_slippage,
        ))

        print("liquidity", quote.liquidity)
        print("est_token_a", quote.token_est_a)
        print("est_token_b", quote.token_est_b)
        print("min_token_a", quote.token_min_a)
        print("min_token_a", quote.token_min_b)

        tx.add_instruction(WhirlpoolIx.decrease_liquidity(
            ctx.program_id,
            DecreaseLiquidityParams(
                liquidity_amount=quote.liquidity,
                token_min_a=quote.token_min_a,
                token_min_b=quote.token_min_b,
                # accounts
                whirlpool=position.whirlpool,
                position=position_pubkey,
                position_token_account=position_ata,
                position_authority=ctx.wallet.pubkey(),
                token_owner_account_a=token_account_map[str(whirlpool.token_mint_a)],
                token_owner_account_b=token_account_map[str(whirlpool.token_mint_b)],
                token_vault_a=whirlpool.token_vault_a,
                token_vault_b=whirlpool.token_vault_b,
                tick_array_lower=ta_lower_pubkey,
                tick_array_upper=ta_upper_pubkey,
            )
        ))

    # collect fees
    tx.add_instruction(WhirlpoolIx.collect_fees(
        ctx.program_id,
        CollectFeesParams(
            whirlpool=position.whirlpool,
            position_authority=ctx.wallet.pubkey(),
            position=position_pubkey,
            position_token_account=position_ata,
            token_owner_account_a=token_account_map[str(whirlpool.token_mint_a)],
            token_vault_a=whirlpool.token_vault_a,
            token_owner_account_b=token_account_map[str(whirlpool.token_mint_b)],
            token_vault_b=whirlpool.token_vault_b,
        )
    ))

    # collect rewards
    for reward_index, ri in enumerate(whirlpool.reward_infos):
        if PoolUtil.is_reward_initialized(ri):
            tx.add_instruction(WhirlpoolIx.collect_reward(
                ctx.program_id,
                CollectRewardParams(
                    reward_index=reward_index,
                    whirlpool=position.whirlpool,
                    position_authority=ctx.wallet.pubkey(),
                    position=position_pubkey,
                    position_token_account=position_ata,
                    reward_owner_account=token_account_map[str(ri.mint)],
                    reward_vault=ri.vault,
                )
            ))

    # close position
    tx.add_instruction(WhirlpoolIx.close_position_with_token_extensions(
        ctx.program_id,
        ClosePositionWithTokenExtensionsParams(
            position_authority=ctx.wallet.pubkey(),
            receiver=ctx.wallet.pubkey(),
            position=position_pubkey,
            position_mint=position.position_mint,
            position_token_account=position_ata,
        )
    ))

    # add priority fee
    cu = 200000
    pf_in_lamports = 20000
    tx.set_compute_unit_limit(cu)
    tx.set_compute_unit_price(int(pf_in_lamports * 10**6 / cu))

    # execute
    signature = await tx.build_and_execute()
    print("TX signature", signature)

asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python this_script.py

wallet pubkey r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6
position pubkey 6acPePn5gAJz4SD9jNWqJKGvfo4oAT7cGUshtBqeEDTg
whirlpool token_mint_a 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
whirlpool token_mint_b EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
whirlpool tick_spacing 64
whirlpool tick_current_index -118401
whirlpool sqrt_price 49547210208153008
whirlpool price 0.007214
liquidity 12788777
est_token_a 1402038475
est_token_b 9958
min_token_a 1388018090
min_token_a 9858
TX signature 54yjbnTHDmEUD4UrDWGWmKgywBZBWvicfJWBrULfaGcstSRnChmBpbMQ5um5yMadojjgpWemq5jPgY5qGw5fuFEY

"""