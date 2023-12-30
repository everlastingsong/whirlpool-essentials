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
SAMO_USDC_WHIRLPOOL_PUBKEY = Pubkey.from_string("9vqYJjDUFecLL2xPUC4Rc7hyCtZ6iJ4mDiVZX7aFXoAe")


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
    sqrt_price_limit = SwapUtil.get_default_sqrt_price_limit(direction)
    acceptable_slippage = Percentage.from_fraction(1, 100)  # 1%

    # get ATA (not considering WSOL and creation of ATA)
    token_account_a = TokenUtil.derive_ata(keypair.pubkey(), whirlpool.token_mint_a)
    token_account_b = TokenUtil.derive_ata(keypair.pubkey(), whirlpool.token_mint_b)
    print("token_account_a", token_account_a)
    print("token_account_b", token_account_b)

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
            token_owner_account_a=token_account_a,
            token_vault_a=whirlpool.token_vault_a,
            token_owner_account_b=token_account_b,
            token_vault_b=whirlpool.token_vault_b,
            tick_array_0=quote.tick_array_0,
            tick_array_1=quote.tick_array_1,
            tick_array_2=quote.tick_array_2,
            oracle=oracle,
        )
    )
    tx = TransactionBuilder(ctx.connection, keypair).add_instruction(ix)

    # add priority fees (+ 1000 lamports)
    tx.set_compute_unit_limit(200000)
    tx.set_compute_unit_price(int(1000 * 10**6 / 200000))

    signature = await tx.build_and_execute()
    print("TX signature", signature)

asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python essentials_swap_with_priority_fee.py
wallet pubkey r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6
whirlpool token_mint_a 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
whirlpool token_mint_b EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
whirlpool tick_spacing 64
whirlpool tick_current_index -112957
whirlpool sqrt_price 65045450509082362
whirlpool price 0.012434
token_account_a 6dM4iMgSei6zF9y3sqdgSJ2xwNXML5wk5QKhV4DqJPhu
token_account_b FbQdXCQgGQYj3xcGeryVVFjKCTsAuu53vmCRtmjQEqM5
tickarrays [Pubkey(
    4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G,
), Pubkey(
    CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH,
), Pubkey(
    EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ,
)]
oracle 5HyJnjQ4XTSVXUS2Q8Ef6VCVwnXGnHE2WTwq7iSaZJez
SwapQuote(amount=10000, other_amount_threshold=793844968, sqrt_price_limit=79226673515401279992447579055, direction=<SwapDirection.BtoA: 'B to A'>, specified_amount=<SpecifiedAmount.SwapInput: 'Swap Input'>, tick_array_0=Pubkey(
    4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G,
), tick_array_1=Pubkey(
    CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH,
), tick_array_2=Pubkey(
    CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH,
), estimated_amount_in=10000, estimated_amount_out=801863605, estimated_end_tick_index=-112957, estimated_end_sqrt_price=65045487802052615, estimated_fee_amount=30)
amount 10000
other_amount_threshold 793844968
slippage 1/100
direction SwapDirection.BtoA
specified_amount SpecifiedAmount.SwapInput
tick_arrays 4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH
TX signature myHJWgEJoKh9pK5QrEqKrdEoZSsgL358BARgbRnCKbxBnLFjrM8e7sL3CEM6H1ctfjtYX4VUFdBFKeDQU4hd3eb
"""