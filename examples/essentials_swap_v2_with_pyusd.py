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
from orca_whirlpool.utils import DecimalUtil, PriceMath, SwapUtil, PDAUtil, TokenUtil
from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID
from orca_whirlpool.instruction import WhirlpoolIx, SwapV2Params
from orca_whirlpool.transaction import TransactionBuilder
from orca_whirlpool.quote import QuoteBuilder, SwapQuoteParams
from orca_whirlpool.types import Percentage, SwapDirection, SpecifiedAmount, TickArrayReduction

load_dotenv()
RPC_ENDPOINT_URL = os.getenv("RPC_ENDPOINT_URL")
SOL_PYUSD_WHIRLPOOL_PUBKEY = Pubkey.from_string("6Wfzz7Xczn4pciH4LnvF79r34htiWpTXNPCFz4jWZpi3")

#
# CAUTION
#
# whirlpool-essentials can handle v2 instructions.
# HOWEVER quote functions cannot handle TransferFee extension yet.
# So please ensure that input and output token don't use TransferFee extension.
# (If its fee rate is zero, it can be ignored)
#


async def main():
    # read wallet
    # - how to create: solana-keygen new -o wallet.json
    # - need some USDC and SAMO
    with Path("wallet.json").open() as f:
        keypair = Keypair.from_bytes(bytes(json.load(f)))
    print("wallet pubkey", keypair.pubkey())

    # create Anchor client
    connection = AsyncClient(RPC_ENDPOINT_URL)
    ctx = WhirlpoolContext(ORCA_WHIRLPOOL_PROGRAM_ID, connection, keypair)

    # get whirlpool
    whirlpool_pubkey = SOL_PYUSD_WHIRLPOOL_PUBKEY
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
    amount = DecimalUtil.to_u64(Decimal("0.0001"), token_a_decimal)  # SOL
    direction = SwapDirection.AtoB
    specified_amount = SpecifiedAmount.SwapInput
    other_amount_threshold = 0
    sqrt_price_limit = SwapUtil.get_default_sqrt_price_limit(direction)
    acceptable_slippage = Percentage.from_fraction(1, 100)  # 1%

    # get TickArray
    pubkeys = SwapUtil.get_tick_array_pubkeys(
        whirlpool.tick_current_index,
        whirlpool.tick_spacing,
        direction,
        ctx.program_id,
        whirlpool_pubkey
    )
    print("tickarrays", pubkeys)

    # get Oracle
    oracle = PDAUtil.get_oracle(ctx.program_id, whirlpool_pubkey).pubkey
    print("oracle", oracle)

    # get quote
    tick_arrays = await ctx.fetcher.list_tick_arrays(pubkeys)
    quote = QuoteBuilder.swap(SwapQuoteParams(
        whirlpool=whirlpool,
        amount=amount,
        other_amount_threshold=other_amount_threshold,
        sqrt_price_limit=sqrt_price_limit,
        direction=direction,
        specified_amount=specified_amount,
        tick_arrays=tick_arrays,
        slippage_tolerance=acceptable_slippage,
    ), TickArrayReduction.Conservative)
    print(quote)
    print("amount", quote.amount)
    print("other_amount_threshold", quote.other_amount_threshold)
    print("slippage", acceptable_slippage)
    print("direction", quote.direction)
    print("specified_amount", quote.specified_amount)
    print("tick_arrays", quote.tick_array_0, quote.tick_array_1, quote.tick_array_2)

    # get ATA (create if needed)
    token_account_a = await TokenUtil.resolve_or_create_ata(ctx.connection, ctx.wallet.pubkey(), whirlpool.token_mint_a, quote.amount if quote.direction.is_a_to_b else 0)
    token_account_b = await TokenUtil.resolve_or_create_ata(ctx.connection, ctx.wallet.pubkey(), whirlpool.token_mint_b, quote.amount if quote.direction.is_b_to_a else 0)
    print("token_account_a", token_account_a.pubkey)
    print("token_account_b", token_account_b.pubkey)

    # get token programs
    mints = await ctx.fetcher.list_token_mints([
        whirlpool.token_mint_a,
        whirlpool.token_mint_b,
    ])

    # execute transaction
    ix = WhirlpoolIx.swap_v2(
        ctx.program_id,
        SwapV2Params(
            amount=quote.amount,
            other_amount_threshold=quote.other_amount_threshold,
            sqrt_price_limit=sqrt_price_limit,
            amount_specified_is_input=specified_amount.is_swap_input,
            a_to_b=direction.is_a_to_b,
            token_authority=keypair.pubkey(),
            whirlpool=whirlpool_pubkey,
            token_owner_account_a=token_account_a.pubkey,
            token_vault_a=whirlpool.token_vault_a,
            token_owner_account_b=token_account_b.pubkey,
            token_vault_b=whirlpool.token_vault_b,
            tick_array_0=quote.tick_array_0,
            tick_array_1=quote.tick_array_1,
            tick_array_2=quote.tick_array_2,
            oracle=oracle,
            # V2 specific
            token_mint_a=whirlpool.token_mint_a,
            token_mint_b=whirlpool.token_mint_b,
            token_program_a=mints[0].token_program_id,
            token_program_b=mints[1].token_program_id,
        )
    )
    tx = TransactionBuilder(ctx.connection, keypair)\
        .add_instruction(token_account_a.instruction)\
        .add_instruction(token_account_b.instruction)\
        .add_instruction(ix)

    # add priority fees (+ 1000 lamports)
    tx.set_compute_unit_limit(200000)
    tx.set_compute_unit_price(int(1000 * 10**6 / 200000))

    signature = await tx.build_and_execute()
    print("TX signature", signature)

asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python this_script.py

wallet pubkey r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6
whirlpool token_mint_a So11111111111111111111111111111111111111112
whirlpool token_mint_b 2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo
whirlpool tick_spacing 16
whirlpool tick_current_index -15936
whirlpool sqrt_price 8315684201453356325
whirlpool price 203.215360
tickarrays [Pubkey(
    Hpjd67EuV2aPh6fp3NEFHEZp89VTV2Vxovvk8xvFGMz6,
), Pubkey(
    8Xb9QTCL3zoEJCB6iYmJRSgKuDK3vDgYkScxQjH5Gq3j,
), Pubkey(
    BLW5mXg11kbKQo7GTrMuNbMu3gyKk9DNhZFRcaPEgYKi,
)]
oracle 7wb3gnXzohnjReusRjCxPN5Q671GwproWcr3hTrr6rQW
SwapQuote(amount=100000, other_amount_threshold=20086, sqrt_price_limit=4295048016, direction=<SwapDirection.AtoB: 'A to B'>, specified_amount=<SpecifiedAmount.SwapInput: 'Swap Input'>, tick_array_0=Pubkey(
    Hpjd67EuV2aPh6fp3NEFHEZp89VTV2Vxovvk8xvFGMz6,
), tick_array_1=Pubkey(
    8Xb9QTCL3zoEJCB6iYmJRSgKuDK3vDgYkScxQjH5Gq3j,
), tick_array_2=Pubkey(
    8Xb9QTCL3zoEJCB6iYmJRSgKuDK3vDgYkScxQjH5Gq3j,
), estimated_amount_in=100000, estimated_amount_out=20289, estimated_end_tick_index=-15936, estimated_end_sqrt_price=8315675550016017065, estimated_fee_amount=160)
amount 100000
other_amount_threshold 20086
slippage 1/100
direction SwapDirection.AtoB
specified_amount SpecifiedAmount.SwapInput
tick_arrays Hpjd67EuV2aPh6fp3NEFHEZp89VTV2Vxovvk8xvFGMz6 8Xb9QTCL3zoEJCB6iYmJRSgKuDK3vDgYkScxQjH5Gq3j 8Xb9QTCL3zoEJCB6iYmJRSgKuDK3vDgYkScxQjH5Gq3j
token_account_a 7FEc93YbuyvR6M2orVSpsnoX2s5EYcR1uQoLv1BYtLFu
token_account_b 2A7Cc48jwWWoixM5CWquQKEqk9KNQvY2Xw3WJbBRc6Ei
TX signature 4SHyT5NtWu6i1Tu7WB3V1SN4KBKUTroCAAkce6aALrCkPkBq6zPC8cmSetuAaD21LRmrrY3QGYoL7HmNitEsUgNF

"""