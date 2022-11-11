# ATTENTION!
#
# to use this script, you need to create wallet.json
# and it holds some USDC (>= 0.1) and SAMO (>= 1)
#
# solana related library:
#   - solders   ( >= 0.9.3  )
#   - solana    ( >= 0.27.2 )
#   - anchorpy  ( >= 0.11.0 )
#
# NOTE!
# whirlpool_essentials is in a very early stage and is subject to change, including breaking changes.
#
import asyncio
import json
import os
from dotenv import load_dotenv
from typing import List
from decimal import Decimal
from pathlib import Path
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey
from solana.keypair import Keypair

# ported functions from whirlpools-sdk and common-sdk
from orca_whirlpool.context import WhirlpoolContext
from orca_whirlpool.utils import DecimalUtil, PriceMath, SwapUtil, PDAUtil, TokenUtil
from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID
from orca_whirlpool.instruction import WhirlpoolIx, SwapParams
from orca_whirlpool.transaction import TransactionBuilder
from orca_whirlpool.quote import QuoteBuilder, SwapQuote, SwapQuoteParams
from orca_whirlpool.types import Percentage, KeyedTickArray, SwapDirection, SpecifiedAmount

load_dotenv()
RPC_ENDPOINT_URL = os.getenv("RPC_ENDPOINT_URL")
SAMO_USDC_WHIRLPOOL_PUBKEY = PublicKey("9vqYJjDUFecLL2xPUC4Rc7hyCtZ6iJ4mDiVZX7aFXoAe")


async def get_tick_arrays(ctx: WhirlpoolContext, pubkeys: List[PublicKey]) -> List[KeyedTickArray]:
    fetched = await ctx.fetcher.list_tick_arrays(pubkeys, True)
    return [KeyedTickArray(pubkey, data) for pubkey, data in zip(pubkeys, fetched)]


async def main():
    # read wallet
    # - how to create: solana-keygen new -o wallet.json
    # - need some USDC and SAMO
    with Path("wallet.json").open() as f:
        keypair = Keypair.from_secret_key(bytes(json.load(f)))
    print("wallet pubkey", keypair.public_key)

    # create Anchor client
    connection = AsyncClient(RPC_ENDPOINT_URL)
    ctx = WhirlpoolContext(ORCA_WHIRLPOOL_PROGRAM_ID, connection, keypair)

    # get whirlpool
    whirlpool_pubkey = SAMO_USDC_WHIRLPOOL_PUBKEY
    whirlpool = await ctx.fetcher.get_whirlpool(whirlpool_pubkey)
    token_a_decimal = (await ctx.fetcher.get_token_mint(whirlpool.token_mint_a)).decimals  # SAMO_DECIMAL
    token_b_decimal = (await ctx.fetcher.get_token_mint(whirlpool.token_mint_b)).decimals  # USDC_DECIMAL
    print("whirlpool token_mint_a", whirlpool.token_mint_a)
    print("whirlpool token_mint_b", whirlpool.token_mint_b)
    print("whirlpool tick_spacing", whirlpool.tick_spacing)
    print("whirlpool tick_current_index", whirlpool.tick_current_index)
    print("whirlpool sqrt_price", whirlpool.sqrt_price)
    price = PriceMath.sqrt_price_x64_to_price(whirlpool.sqrt_price, token_a_decimal, token_b_decimal)
    print("whirlpool price", DecimalUtil.to_fixed(price, token_b_decimal))

    # input
    # no threshold because it is difficult to port swap quote function ^^;
    amount = DecimalUtil.to_u64(Decimal("0.01"), token_b_decimal)  # USDC
    direction = SwapDirection.BtoA
    specified_amount = SpecifiedAmount.SwapInput
    other_amount_threshold = 0
    sqrt_price_limit = SwapUtil.get_default_sqrt_price_limit(direction.is_a_to_b)
    acceptable_slippage = Percentage.from_fraction(0, 100)  # 0% = exact

    # get ATA (not considering WSOL and creation of ATA)
    token_account_a = TokenUtil.derive_ata(keypair.public_key, whirlpool.token_mint_a)
    token_account_b = TokenUtil.derive_ata(keypair.public_key, whirlpool.token_mint_b)
    print("token_account_a", token_account_a)
    print("token_account_b", token_account_b)

    # get TickArray
    pubkeys = SwapUtil.get_tick_array_pubkeys(
        whirlpool.tick_current_index,
        whirlpool.tick_spacing,
        direction.is_a_to_b,
        ctx.program_id,
        whirlpool_pubkey
    )
    print("tickarrays", pubkeys)

    # get Oracle
    oracle = PDAUtil.get_oracle(ctx.program_id, whirlpool_pubkey).pubkey
    print("oracle", oracle)

    # get quote
    keyed_tick_arrays = await get_tick_arrays(ctx, pubkeys)

    quote = QuoteBuilder.swap(SwapQuoteParams(
        whirlpool=whirlpool,
        amount=amount,
        other_amount_threshold=other_amount_threshold,
        sqrt_price_limit=sqrt_price_limit,
        direction=direction,
        specified_amount=specified_amount,
        tick_array_0=keyed_tick_arrays[0],
        tick_array_1=keyed_tick_arrays[1],
        tick_array_2=keyed_tick_arrays[2],
        slippage_tolerance=acceptable_slippage,
    ))
    print(quote)

    # execute transaction
    ix = WhirlpoolIx.swap(
        ctx.program_id,
        SwapParams(
            amount=amount,
            other_amount_threshold=other_amount_threshold,
            sqrt_price_limit=sqrt_price_limit,
            amount_specified_is_input=specified_amount.is_swap_input,
            a_to_b=direction.is_a_to_b,
            token_authority=keypair.public_key,
            whirlpool=whirlpool_pubkey,
            token_owner_account_a=token_account_a,
            token_vault_a=whirlpool.token_vault_a,
            token_owner_account_b=token_account_b,
            token_vault_b=whirlpool.token_vault_b,
            tick_array_0=pubkeys[0],
            tick_array_1=pubkeys[1],
            tick_array_2=pubkeys[2],
            oracle=oracle,
        )
    )
    tx = TransactionBuilder(ctx.connection, keypair).add_instruction(ix)
    signature = await tx.build_and_execute()
    print("TX signature", signature)

asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python essentials_swap.py
wallet pubkey r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6
whirlpool token_mint_a 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
whirlpool token_mint_b EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
whirlpool tick_spacing 64
whirlpool tick_current_index -116826
whirlpool sqrt_price 53604644321225494
whirlpool price 0.008444
token_account_a 6dM4iMgSei6zF9y3sqdgSJ2xwNXML5wk5QKhV4DqJPhu
token_account_b FbQdXCQgGQYj3xcGeryVVFjKCTsAuu53vmCRtmjQEqM5
tickarrays [4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G, CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH, EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ]
oracle 5HyJnjQ4XTSVXUS2Q8Ef6VCVwnXGnHE2WTwq7iSaZJez
TX signature 41nnMC8zCu7nycUPJ6zG4edEfMihV85i4iVBV2Th2XZTQiJYnsDVxCvsgM2giwnKxZSm9YHQLMJPxKv7RzdP2izE
"""