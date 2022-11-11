import dataclasses
from ...errors import WhirlpoolError, SwapErrorCode, MathErrorCode
from ...types.enums import SwapDirection, SpecifiedAmount
from ...utils.liquidity_math import LiquidityMath
from ...utils.q64_fixed_point_math import Q64FixedPointMath
from ...constants import FEE_RATE_MUL_VALUE, MIN_SQRT_PRICE, MAX_SQRT_PRICE
from .bit_math import BitMath


@dataclasses.dataclass(frozen=True)
class SwapStep:
    amount_in: int
    amount_out: int
    next_sqrt_price: int
    fee_amount: int


def get_fixed_amount_delta(
    liquidity: int,
    sqrt_price_0: int,
    sqrt_price_1: int,
    specified_amount: SpecifiedAmount,
    direction: SwapDirection,
) -> int:
    round_up = specified_amount.is_swap_input
    if specified_amount.is_a(direction):
        return LiquidityMath.get_token_a_from_liquidity(liquidity, sqrt_price_0, sqrt_price_1, round_up)
    else:
        return LiquidityMath.get_token_b_from_liquidity(liquidity, sqrt_price_0, sqrt_price_1, round_up)


def get_unfixed_amount_delta(
    liquidity: int,
    sqrt_price_0: int,
    sqrt_price_1: int,
    specified_amount: SpecifiedAmount,
    direction: SwapDirection,
) -> int:
    round_up = specified_amount.is_swap_output
    if specified_amount.is_a(direction):
        return LiquidityMath.get_token_b_from_liquidity(liquidity, sqrt_price_0, sqrt_price_1, round_up)
    else:
        return LiquidityMath.get_token_a_from_liquidity(liquidity, sqrt_price_0, sqrt_price_1, round_up)


def get_next_sqrt_price_from_a_round_up(
    sqrt_price: int,
    liquidity: int,
    amount: int,
    specified_amount: SpecifiedAmount,
) -> int:
    if amount == 0:
        return sqrt_price

    # case1) sqrt_price > next_sqrt_price [amount is input, price down]
    #   -amount = L / sqrt_price/x64 - L / next_sqrt_price/x64
    #   L / next_sqrt_price/x64 = L / sqrt_price/x64 + amount
    #   L / next_sqrt_price/x64 = (L + amount*sqrt_price/x64) / sqrt_price/x64
    #   next_sqrt_price/x64 / L = sqrt_price/x64 / (L + amount*sqrt_price/x64)
    #   next_sqrt_price = L*sqrt_price / (L + amount*sqrt_price/x64)
    #   next_sqrt_price = L*sqrt_price*x64 / (L*x64 + amount*sqrt_price)
    #
    # case2) sqrt_price < next_sqrt_price [amount is output, price up]
    #   amount = L / sqrt_price/x64 - L / next_sqrt_price/x64
    #   L / next_sqrt_price/x64 = L / sqrt_price/x64 - amount
    #   L / next_sqrt_price/x64 = (L - amount*sqrt_price/x64) / sqrt_price/x64
    #   next_sqrt_price/x64 / L = sqrt_price/x64 / (L - amount*sqrt_price/x64)
    #   next_sqrt_price = L*sqrt_price / (L - amount*sqrt_price/x64)
    #   next_sqrt_price = L*sqrt_price*x64 / (L*x64 - amount*sqrt_price)
    shift_x64 = 2**64
    numerator = liquidity * sqrt_price * shift_x64
    if BitMath.is_over_limit(numerator, 256):
        raise WhirlpoolError(MathErrorCode.MultiplicationOverflow)

    liquidity_x64 = liquidity * shift_x64
    amount_sqrt_price = amount * sqrt_price
    if specified_amount.is_swap_input:
        denominator = liquidity_x64 + amount_sqrt_price
    else:
        if amount_sqrt_price >= liquidity_x64:
            raise WhirlpoolError(MathErrorCode.DivideByZero)
        denominator = liquidity_x64 - amount_sqrt_price

    next_sqrt_price = BitMath.div_round_up(numerator, denominator)
    if next_sqrt_price < MIN_SQRT_PRICE:
        raise WhirlpoolError(SwapErrorCode.SqrtPriceMinSubceeded)
    if next_sqrt_price > MAX_SQRT_PRICE:
        raise WhirlpoolError(SwapErrorCode.SqrtPriceMaxExceeded)
    return next_sqrt_price


def get_next_sqrt_price_from_b_round_down(
    sqrt_price: int,
    liquidity: int,
    amount: int,
    specified_amount: SpecifiedAmount,
) -> int:
    # amount = L*abs(sqrt_price/x64 - next_sqrt_price/x64)
    # amount*x64 = L*abs(sqrt_price - next_sqrt_price)
    # delta = abs(sqrt_price - next_sqrt_price) = amount*x64 / L
    round_up = specified_amount.is_swap_output
    amount_x64 = Q64FixedPointMath.int_to_x64int(amount)
    delta = BitMath.div_round_up_if(amount_x64, liquidity, round_up)

    if specified_amount.is_swap_input:
        return sqrt_price + delta
    else:
        return sqrt_price - delta


def get_next_sqrt_price(
    sqrt_price: int,
    liquidity: int,
    amount: int,
    specified_amount: SpecifiedAmount,
    direction: SwapDirection,
) -> int:
    if specified_amount.is_a(direction):
        return get_next_sqrt_price_from_a_round_up(sqrt_price, liquidity, amount, specified_amount)
    else:
        return get_next_sqrt_price_from_b_round_down(sqrt_price, liquidity, amount, specified_amount)


def get_fee_amount(fee_less_amount: int, fee_rate) -> int:
    return BitMath.mul_div_round_up(fee_less_amount, fee_rate, FEE_RATE_MUL_VALUE - fee_rate, 128)


def get_fee_less_amount(amount: int, fee_rate) -> int:
    return BitMath.mul_div(amount, FEE_RATE_MUL_VALUE - fee_rate, FEE_RATE_MUL_VALUE, 128)


def compute_swap_step(
    remaining_amount: int,
    fee_rate: int,
    liquidity: int,
    sqrt_price: int,
    target_sqrt_price: int,
    specified_amount: SpecifiedAmount,
    direction: SwapDirection,
) -> SwapStep:
    if specified_amount.is_swap_input:
        consumable_amount = get_fee_less_amount(remaining_amount, fee_rate)
    else:
        consumable_amount = remaining_amount

    fixed_amount_delta = get_fixed_amount_delta(liquidity, sqrt_price, target_sqrt_price, specified_amount, direction)
    if consumable_amount >= fixed_amount_delta:
        is_max_swap = True
        next_sqrt_price = target_sqrt_price
    else:
        is_max_swap = False
        next_sqrt_price = get_next_sqrt_price(sqrt_price, liquidity, consumable_amount, specified_amount, direction)

    fixed_amount_delta = get_fixed_amount_delta(liquidity, sqrt_price, next_sqrt_price, specified_amount, direction)
    unfixed_amount_delta = get_unfixed_amount_delta(liquidity, sqrt_price, next_sqrt_price, specified_amount, direction)
    if specified_amount.is_swap_input:
        amount_in = fixed_amount_delta
        amount_out = unfixed_amount_delta
    else:
        amount_in = unfixed_amount_delta
        amount_out = fixed_amount_delta

    # cap for exact out swap
    if specified_amount.is_swap_output and amount_out > remaining_amount:
        amount_out = remaining_amount

    if specified_amount.is_swap_input and not is_max_swap:
        fee_amount = remaining_amount - amount_in
    else:
        fee_amount = get_fee_amount(amount_in, fee_rate)

    return SwapStep(
        amount_in=amount_in,
        amount_out=amount_out,
        next_sqrt_price=next_sqrt_price,
        fee_amount=fee_amount,
    )
