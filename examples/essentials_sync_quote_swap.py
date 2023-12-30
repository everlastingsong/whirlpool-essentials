import os
from dotenv import load_dotenv
from decimal import Decimal
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.keypair import Keypair

from sync_account_fetcher import SyncAccountFetcher
from orca_whirlpool.utils import DecimalUtil, PriceMath, SwapUtil, PDAUtil, TokenUtil
from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID
from orca_whirlpool.quote import QuoteBuilder, SwapQuoteParams
from orca_whirlpool.types import Percentage, SwapDirection, SpecifiedAmount, TickArrayReduction

load_dotenv()
RPC_ENDPOINT_URL = os.getenv("RPC_ENDPOINT_URL")
SAMO_USDC_WHIRLPOOL_PUBKEY = Pubkey.from_string("9vqYJjDUFecLL2xPUC4Rc7hyCtZ6iJ4mDiVZX7aFXoAe")


def main():
    # use dummy wallet
    keypair = Keypair()

    # create Anchor client
    connection = Client(RPC_ENDPOINT_URL)
    # ctx
    fetcher = SyncAccountFetcher(connection)
    program_id = ORCA_WHIRLPOOL_PROGRAM_ID

    # get whirlpool
    whirlpool_pubkey = SAMO_USDC_WHIRLPOOL_PUBKEY
    whirlpool = fetcher.get_whirlpool(whirlpool_pubkey)
    token_a_decimal = (fetcher.get_token_mint(whirlpool.token_mint_a)).decimals  # SAMO_DECIMAL
    token_b_decimal = (fetcher.get_token_mint(whirlpool.token_mint_b)).decimals  # USDC_DECIMAL
    print("whirlpool token_mint_a", whirlpool.token_mint_a)
    print("whirlpool token_mint_b", whirlpool.token_mint_b)
    print("whirlpool tick_spacing", whirlpool.tick_spacing)
    print("whirlpool tick_current_index", whirlpool.tick_current_index)
    print("whirlpool sqrt_price", whirlpool.sqrt_price)
    price = PriceMath.sqrt_price_x64_to_price(whirlpool.sqrt_price, token_a_decimal, token_b_decimal)
    print("whirlpool price", DecimalUtil.to_fixed(price, token_b_decimal))

    # input
    amount = DecimalUtil.to_u64(Decimal("100"), token_b_decimal)  # USDC
    direction = SwapDirection.BtoA
    specified_amount = SpecifiedAmount.SwapInput
    other_amount_threshold = 0
    sqrt_price_limit = SwapUtil.get_default_sqrt_price_limit(direction)
    acceptable_slippage = Percentage.from_fraction(1, 100)  # 1%

    # get TickArray
    pubkeys = SwapUtil.get_tick_array_pubkeys(
        whirlpool.tick_current_index,
        whirlpool.tick_spacing,
        direction,
        program_id,
        whirlpool_pubkey
    )
    print("tickarrays", pubkeys)

    # get quote
    tick_arrays = fetcher.list_tick_arrays(pubkeys)
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
    print("price before trade", PriceMath.sqrt_price_x64_to_price(whirlpool.sqrt_price, token_a_decimal, token_b_decimal))
    print("price after trade", PriceMath.sqrt_price_x64_to_price(quote.estimated_end_sqrt_price, token_a_decimal, token_b_decimal))


main()

"""
SAMPLE OUTPUT:

$ python essentials_quote_swap.py
whirlpool token_mint_a 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
whirlpool token_mint_b EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
whirlpool tick_spacing 64
whirlpool tick_current_index -127810
whirlpool sqrt_price 30954288334991641
whirlpool price 0.002816
tickarrays [ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq, Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT, 4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G]
SwapQuote(amount=100000000, other_amount_threshold=34788485701121, sqrt_price_limit=79226673515401279992447579055, direction=<SwapDirection.BtoA: 'B to A'>, specified_amount=<SpecifiedAmount.SwapInput: 'Swap Input'>, tick_array_0=ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq, tick_array_1=Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT, tick_array_2=Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT, estimated_amount_in=100000000, estimated_amount_out=35139884546587, estimated_end_tick_index=-127658, estimated_end_sqrt_price=31189725685457391, estimated_fee_amount=300001)
amount 100000000
other_amount_threshold 34788485701121
slippage 1/100
direction SwapDirection.BtoA
specified_amount SpecifiedAmount.SwapInput
tick_arrays ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT
price before trade 0.002815802578887143032313588563
price after trade 0.002858799288180870045611782753
"""