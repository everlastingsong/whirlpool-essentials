import dataclasses
from typing import List, Optional
from solders.pubkey import Pubkey
from ...accounts.types import TickArray, Whirlpool
from ...types.enums import SwapDirection, SpecifiedAmount
from ...types.percentage import Percentage


@dataclasses.dataclass(frozen=True)
class SwapQuoteParams:
    whirlpool: Whirlpool
    amount: int
    other_amount_threshold: int
    sqrt_price_limit: int
    direction: SwapDirection
    specified_amount: SpecifiedAmount
    tick_arrays: List[Optional[TickArray]]
    slippage_tolerance: Percentage


@dataclasses.dataclass(frozen=True)
class SwapQuote:
    # SwapInput
    amount: int
    other_amount_threshold: int
    sqrt_price_limit: int
    direction: SwapDirection
    specified_amount: SpecifiedAmount
    tick_array_0: Pubkey
    tick_array_1: Pubkey
    tick_array_2: Pubkey
    # SwapQuote
    estimated_amount_in: int
    estimated_amount_out: int
    estimated_end_tick_index: int
    estimated_end_sqrt_price: int
    estimated_fee_amount: int
