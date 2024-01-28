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
from orca_whirlpool.instruction import WhirlpoolIx, SwapParams
from orca_whirlpool.transaction import TransactionBuilder
from orca_whirlpool.quote import QuoteBuilder, SwapQuoteParams
from orca_whirlpool.types import Percentage, SwapDirection, SpecifiedAmount, TickArrayReduction

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

    # create Anchor client
    connection = AsyncClient(RPC_ENDPOINT_URL)
    ctx = WhirlpoolContext(ORCA_WHIRLPOOL_PROGRAM_ID, connection, keypair)

    # get whirlpool
    whirlpool_pubkey = SOL_USDC_WHIRLPOOL_PUBKEY
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

    # get ATA and temporary SOL account (create if needed)
    token_account_a = await TokenUtil.resolve_or_create_ata(ctx.connection, ctx.wallet.pubkey(), whirlpool.token_mint_a, quote.amount if quote.direction.is_a_to_b else 0)
    token_account_b = await TokenUtil.resolve_or_create_ata(ctx.connection, ctx.wallet.pubkey(), whirlpool.token_mint_b, quote.amount if quote.direction.is_b_to_a else 0)
    print("token_account_a", token_account_a.pubkey)
    print("token_account_b", token_account_b.pubkey)

    # execute transaction
    ix = WhirlpoolIx.swap(
        ctx.program_id,
        SwapParams(
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
        )
    )
    tx = TransactionBuilder(ctx.connection, keypair) \
        .add_instruction(token_account_a.instruction) \
        .add_instruction(token_account_b.instruction) \
        .add_instruction(ix)

    signature = await tx.build_and_execute()
    print("TX signature", signature)

asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python essentials_swap_with_sol.py
wallet pubkey r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6
whirlpool token_mint_a So11111111111111111111111111111111111111112
whirlpool token_mint_b EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
whirlpool tick_spacing 64
whirlpool tick_current_index -23622
whirlpool sqrt_price 5662526911338699098
whirlpool price 94.228247
tickarrays [Pubkey(
    A2W6hiA2nf16iqtbZt9vX8FJbiXjv3DBUG3DgTja61HT,
), Pubkey(
    2Eh8HEeu45tCWxY6ruLLRN6VcTSD7bfshGj7bZA87Kne,
), Pubkey(
    EVqGhR2ukNuqZNfvFFAitrX6UqrRm2r8ayKX9LH9xHzK,
)]
oracle 4GkRbcYg1VKsZropgai4dMf2Nj2PkXNLf43knFpavrSi
SwapQuote(amount=100000, other_amount_threshold=9300, sqrt_price_limit=4295048016, direction=<SwapDirection.AtoB: 'A to B'>, specified_amount=<SpecifiedAmount.SwapInput: 'Swap Input'>, tick_array_0=Pubkey(
    A2W6hiA2nf16iqtbZt9vX8FJbiXjv3DBUG3DgTja61HT,
), tick_array_1=Pubkey(
    2Eh8HEeu45tCWxY6ruLLRN6VcTSD7bfshGj7bZA87Kne,
), tick_array_2=Pubkey(
    2Eh8HEeu45tCWxY6ruLLRN6VcTSD7bfshGj7bZA87Kne,
), estimated_amount_in=100000, estimated_amount_out=9394, estimated_end_tick_index=-23622, estimated_end_sqrt_price=5662526827817785379, estimated_fee_amount=300)
amount 100000
other_amount_threshold 9300
slippage 1/100
direction SwapDirection.AtoB
specified_amount SpecifiedAmount.SwapInput
tick_arrays A2W6hiA2nf16iqtbZt9vX8FJbiXjv3DBUG3DgTja61HT 2Eh8HEeu45tCWxY6ruLLRN6VcTSD7bfshGj7bZA87Kne 2Eh8HEeu45tCWxY6ruLLRN6VcTSD7bfshGj7bZA87Kne
token_account_a 4DbScBKeKV4BpKNcM5udxnkxR7dPzN6xbBiu261Wx1zh
token_account_b FbQdXCQgGQYj3xcGeryVVFjKCTsAuu53vmCRtmjQEqM5
TX signature 2HdGUMGBUUeLqR2tyvKckhcLLobAxfxHGYTPtrSMYqpsjZ1mFFsdag99YUfMLbZmxPCJL6jfkMR6Czb7wNh5p86H
"""