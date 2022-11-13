import dataclasses
from ...errors import WhirlpoolError, SwapErrorCode
from ...types.enums import SwapDirection, SpecifiedAmount, TickArrayReduction
from ...accounts.types import Whirlpool
from ...utils.price_math import PriceMath
from ...constants import MIN_SQRT_PRICE, MAX_SQRT_PRICE, MAX_SWAP_TICK_ARRAYS
from .tick_array_sequence import TickArraySequence
from .types import SwapQuoteParams, SwapQuote
from .swap_math import compute_swap_step


@dataclasses.dataclass(frozen=True)
class SwapResult:
    amount_a: int
    amount_b: int
    next_tick_index: int
    next_sqrt_price: int
    fee_amount: int


def compute_swap(
    whirlpool: Whirlpool,
    tick_array_sequence: TickArraySequence,
    amount: int,
    sqrt_price_limit: int,
    specified_amount: SpecifiedAmount,
    direction: SwapDirection,
) -> SwapResult:
    remaining_amount = amount
    calculated_amount = 0

    current_sqrt_price = whirlpool.sqrt_price
    current_liquidity = whirlpool.liquidity
    current_tick_index = whirlpool.tick_current_index

    fee_rate = whirlpool.fee_rate
    total_fee_amount = 0

    while remaining_amount > 0 and current_sqrt_price != sqrt_price_limit:
        next_tick_index = tick_array_sequence.get_next_initialized_tick_index(current_tick_index)
        next_sqrt_price = PriceMath.tick_index_to_sqrt_price_x64(next_tick_index)

        if direction.is_price_down:
            target_sqrt_price = max(next_sqrt_price, sqrt_price_limit)
        else:
            target_sqrt_price = min(next_sqrt_price, sqrt_price_limit)

        swap_computation = compute_swap_step(
            remaining_amount,
            fee_rate,
            current_liquidity,
            current_sqrt_price,
            target_sqrt_price,
            specified_amount,
            direction,
        )

        total_fee_amount += swap_computation.fee_amount
        if specified_amount.is_swap_input:
            remaining_amount -= swap_computation.amount_in
            remaining_amount -= swap_computation.fee_amount
            calculated_amount += swap_computation.amount_out
        else:
            remaining_amount -= swap_computation.amount_out
            calculated_amount += swap_computation.amount_in
            calculated_amount += swap_computation.fee_amount

        if swap_computation.next_sqrt_price != next_sqrt_price:
            current_tick_index = PriceMath.sqrt_price_x64_to_tick_index(swap_computation.next_sqrt_price)
        else:
            next_tick = tick_array_sequence.get_tick(next_tick_index)
            if direction.is_a_to_b:
                current_liquidity -= next_tick.liquidity_net if next_tick.initialized else 0
                current_tick_index = next_tick_index - 1
            else:
                current_liquidity += next_tick.liquidity_net if next_tick.initialized else 0
                current_tick_index = next_tick_index

        current_sqrt_price = swap_computation.next_sqrt_price

    if specified_amount.is_a(direction):
        amount_a = amount - remaining_amount
        amount_b = calculated_amount
    else:
        amount_a = calculated_amount
        amount_b = amount - remaining_amount

    return SwapResult(
        amount_a=amount_a,
        amount_b=amount_b,
        next_tick_index=current_tick_index,
        next_sqrt_price=current_sqrt_price,
        fee_amount=total_fee_amount,
    )


def simulate_swap(params: SwapQuoteParams, tick_array_reduction: TickArrayReduction) -> SwapQuote:
    whirlpool = params.whirlpool
    amount = params.amount
    sqrt_price_limit = params.sqrt_price_limit
    specified_amount = params.specified_amount
    direction = params.direction

    if not MIN_SQRT_PRICE <= sqrt_price_limit <= MAX_SQRT_PRICE:
        raise WhirlpoolError(SwapErrorCode.SqrtPriceOutOfBounds)

    if direction.is_price_down and sqrt_price_limit > whirlpool.sqrt_price:
        raise WhirlpoolError(SwapErrorCode.InvalidSqrtPriceLimitDirection)
    if direction.is_price_up and sqrt_price_limit < whirlpool.sqrt_price:
        raise WhirlpoolError(SwapErrorCode.InvalidSqrtPriceLimitDirection)

    if amount == 0:
        raise WhirlpoolError(SwapErrorCode.ZeroTradableAmount)

    tick_array_sequence = TickArraySequence(
        params.tick_arrays,
        whirlpool.tick_current_index,
        whirlpool.tick_spacing,
        direction,
        MAX_SWAP_TICK_ARRAYS,
    )

    result = compute_swap(
        whirlpool,
        tick_array_sequence,
        amount,
        sqrt_price_limit,
        specified_amount,
        direction,
    )

    if specified_amount.is_swap_input:
        other_amount = result.amount_b if direction.is_a_to_b else result.amount_a
        if other_amount < params.other_amount_threshold:
            raise WhirlpoolError(SwapErrorCode.AmountOutBelowMinimum)
    else:
        other_amount = result.amount_a if direction.is_a_to_b else result.amount_b
        if other_amount > params.other_amount_threshold:
            raise WhirlpoolError(SwapErrorCode.AmountInAboveMaximum)

    if direction.is_a_to_b:
        estimated_amount_in = result.amount_a
        estimated_amount_out = result.amount_b
    else:
        estimated_amount_in = result.amount_b
        estimated_amount_out = result.amount_a

    tick_array_pubkeys = tick_array_sequence.get_tick_array_pubkeys(tick_array_reduction)

    return SwapQuote(
        estimated_amount_in=estimated_amount_in,
        estimated_amount_out=estimated_amount_out,
        estimated_end_tick_index=result.next_tick_index,
        estimated_end_sqrt_price=result.next_sqrt_price,
        estimated_fee_amount=result.fee_amount,
        amount=params.amount,
        other_amount_threshold=params.other_amount_threshold,
        sqrt_price_limit=params.sqrt_price_limit,
        specified_amount=params.specified_amount,
        direction=params.direction,
        tick_array_0=tick_array_pubkeys[0],
        tick_array_1=tick_array_pubkeys[1],
        tick_array_2=tick_array_pubkeys[2],
    )
