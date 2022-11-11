import dataclasses
from solana.publickey import PublicKey
from ...types.types import KeyedTickArray
from ...types.enums import SwapDirection
from ...anchor.accounts import Whirlpool
from ...types.enums import SpecifiedAmount
from ...types.percentage import Percentage


@dataclasses.dataclass(frozen=True)
class SwapQuoteParams:
    whirlpool: Whirlpool
    amount: int
    other_amount_threshold: int
    sqrt_price_limit: int
    direction: SwapDirection
    specified_amount: SpecifiedAmount
    tick_array_0: KeyedTickArray
    tick_array_1: KeyedTickArray
    tick_array_2: KeyedTickArray
    slippage_tolerance: Percentage


@dataclasses.dataclass(frozen=True)
class SwapQuote:
    # SwapInput
    amount: int
    other_amount_threshold: int
    sqrt_price_limit: int
    direction: SwapDirection
    specified_amount: SpecifiedAmount
    tick_array_0: PublicKey
    tick_array_1: PublicKey
    tick_array_2: PublicKey
    # SwapQuote
    estimated_amount_in: int
    estimated_amount_out: int
    estimated_end_tick_index: int
    estimated_end_sqrt_price: int
    estimated_fee_amount: int
