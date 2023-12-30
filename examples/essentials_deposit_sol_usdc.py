import asyncio
import json
import os
from dotenv import load_dotenv
from decimal import Decimal
from pathlib import Path
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair

from orca_whirlpool.context import WhirlpoolContext
from orca_whirlpool.utils import DecimalUtil, PriceMath, PDAUtil, TokenUtil, TickUtil
from orca_whirlpool.types import Percentage
from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID
from orca_whirlpool.instruction import WhirlpoolIx, OpenPositionParams, IncreaseLiquidityParams
from orca_whirlpool.transaction import TransactionBuilder
from orca_whirlpool.quote import QuoteBuilder, IncreaseLiquidityQuoteParams


load_dotenv()
RPC_ENDPOINT_URL = os.getenv("RPC_ENDPOINT_URL")
SOL_USDC_WHIRLPOOL_PUBKEY = Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ")


async def main():
    # read wallet
    # - how to create: solana-keygen new -o wallet.json
    # - need some USDC and SOL
    with Path("wallet.json").open() as f:
        keypair = Keypair.from_bytes(bytes(json.load(f)))
    print("wallet pubkey", keypair.pubkey())

    # create client
    connection = AsyncClient(RPC_ENDPOINT_URL)
    ctx = WhirlpoolContext(ORCA_WHIRLPOOL_PROGRAM_ID, connection, keypair)

    # get whirlpool
    whirlpool_pubkey = SOL_USDC_WHIRLPOOL_PUBKEY
    whirlpool = await ctx.fetcher.get_whirlpool(whirlpool_pubkey)
    decimals_a = (await ctx.fetcher.get_token_mint(whirlpool.token_mint_a)).decimals  # SOL_DECIMAL
    decimals_b = (await ctx.fetcher.get_token_mint(whirlpool.token_mint_b)).decimals  # USDC_DECIMAL
    print("whirlpool token_mint_a", whirlpool.token_mint_a)
    print("whirlpool token_mint_b", whirlpool.token_mint_b)
    print("whirlpool tick_spacing", whirlpool.tick_spacing)
    print("whirlpool tick_current_index", whirlpool.tick_current_index)
    print("whirlpool sqrt_price", whirlpool.sqrt_price)
    price = PriceMath.sqrt_price_x64_to_price(whirlpool.sqrt_price, decimals_a, decimals_b)
    print("whirlpool price", DecimalUtil.to_fixed(price, decimals_b))

    # input
    input_token = whirlpool.token_mint_b  # USDC
    input_amount = DecimalUtil.to_u64(Decimal("0.01"), decimals_b)  # USDC
    acceptable_slippage = Percentage.from_fraction(1, 100)
    price_lower = price / 2
    price_upper = price * 2
    tick_lower_index = PriceMath.price_to_initializable_tick_index(price_lower, decimals_a, decimals_b, whirlpool.tick_spacing)
    tick_upper_index = PriceMath.price_to_initializable_tick_index(price_upper, decimals_a, decimals_b, whirlpool.tick_spacing)

    # get quote
    quote = QuoteBuilder.increase_liquidity_by_input_token(IncreaseLiquidityQuoteParams(
        input_token_mint=input_token,
        input_token_amount=input_amount,
        token_mint_a=whirlpool.token_mint_a,
        token_mint_b=whirlpool.token_mint_b,
        sqrt_price=whirlpool.sqrt_price,
        tick_current_index=whirlpool.tick_current_index,
        tick_lower_index=tick_lower_index,
        tick_upper_index=tick_upper_index,
        slippage_tolerance=acceptable_slippage,
    ))
    print("liquidity", quote.liquidity)
    print("est_token_a", quote.token_est_a)
    print("est_token_b", quote.token_est_b)
    print("max_token_a", quote.token_max_a)
    print("max_token_a", quote.token_max_b)

    # get ATA (considering WSOL)
    token_account_a = await TokenUtil.resolve_or_create_ata(ctx.connection, ctx.wallet.pubkey(), whirlpool.token_mint_a, quote.token_max_a)
    token_account_b = await TokenUtil.resolve_or_create_ata(ctx.connection, ctx.wallet.pubkey(), whirlpool.token_mint_b, quote.token_max_b)
    print("token_account_a", token_account_a.pubkey)
    print("token_account_b", token_account_b.pubkey)

    # build transaction
    tx = TransactionBuilder(ctx.connection, ctx.wallet)

    # WSOL considring
    tx.add_instruction(token_account_a.instruction)
    tx.add_instruction(token_account_b.instruction)

    # open position
    position_mint = Keypair()
    position_ata = TokenUtil.derive_ata(ctx.wallet.pubkey(), position_mint.pubkey())
    position_pda = PDAUtil.get_position(ctx.program_id, position_mint.pubkey())
    open_position_ix = WhirlpoolIx.open_position(
        ctx.program_id,
        OpenPositionParams(
            whirlpool=whirlpool_pubkey,
            tick_lower_index=tick_lower_index,
            tick_upper_index=tick_upper_index,
            position_pda=position_pda,
            position_mint=position_mint.pubkey(),
            position_token_account=position_ata,
            funder=ctx.wallet.pubkey(),
            owner=ctx.wallet.pubkey(),
        )
    )
    tx.add_instruction(open_position_ix)
    tx.add_signer(position_mint)

    # increase liquidity
    tick_array_lower_start_tick_index = TickUtil.get_start_tick_index(tick_lower_index, whirlpool.tick_spacing)
    tick_array_upper_start_tick_index = TickUtil.get_start_tick_index(tick_upper_index, whirlpool.tick_spacing)
    tick_array_lower = PDAUtil.get_tick_array(ctx.program_id, whirlpool_pubkey, tick_array_lower_start_tick_index).pubkey
    tick_array_upper = PDAUtil.get_tick_array(ctx.program_id, whirlpool_pubkey, tick_array_upper_start_tick_index).pubkey
    increase_liquidity_ix = WhirlpoolIx.increase_liquidity(
        ctx.program_id,
        IncreaseLiquidityParams(
            whirlpool=whirlpool_pubkey,
            position=position_pda.pubkey,
            position_token_account=position_ata,
            position_authority=ctx.wallet.pubkey(),
            liquidity_amount=quote.liquidity,
            token_max_a=quote.token_max_a,
            token_max_b=quote.token_max_b,
            token_owner_account_a=token_account_a.pubkey,
            token_owner_account_b=token_account_b.pubkey,
            token_vault_a=whirlpool.token_vault_a,
            token_vault_b=whirlpool.token_vault_b,
            tick_array_lower=tick_array_lower,
            tick_array_upper=tick_array_upper,
        )
    )
    tx.add_instruction(increase_liquidity_ix)

    # execute
    signature = await tx.build_and_execute()
    print("TX signature", signature)

asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python essentials_deposit_sol_usdc.py
wallet pubkey r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6
whirlpool token_mint_a So11111111111111111111111111111111111111112
whirlpool token_mint_b EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
whirlpool tick_spacing 64
whirlpool tick_current_index -34708
whirlpool sqrt_price 3253078221838975758
whirlpool price 31.099225
liquidity 194527
est_token_a 323070
est_token_b 10000
max_token_a 326300
max_token_a 10100
token_account_a 4UaWYZPv76wyVD3NBLR3dhTa5QuDM1xFkMxCK6sRxsSw
token_account_b FbQdXCQgGQYj3xcGeryVVFjKCTsAuu53vmCRtmjQEqM5
TX signature coXNVJ5Wr6FEC4D7c7pqygfhpuNqQVvXqjS5ETm222wZZ9NkqVVuX3k71mbNuqMwKovzRv8h6YPWeDyUXR5G1Qy
"""