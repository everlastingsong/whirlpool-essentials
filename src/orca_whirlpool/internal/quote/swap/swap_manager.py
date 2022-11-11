import dataclasses
from enum import Enum
from typing import List
from solana.publickey import PublicKey
from ...types.types import KeyedTickArray
from ...types.percentage import Percentage
from ...types.enums import SwapDirection, SpecifiedAmount
from ...anchor.accounts import TickArray, Whirlpool
from ...anchor.types import Tick
from ...utils.price_math import PriceMath
from ...utils.liquidity_math import LiquidityMath
from ...utils.q64_fixed_point_math import Q64FixedPointMath
from ...constants import FEE_RATE_MUL_VALUE, MIN_SQRT_PRICE, MAX_SQRT_PRICE, MAX_SWAP_TICK_ARRAYS, MIN_TICK_INDEX, MAX_TICK_INDEX, TICK_ARRAY_SIZE



class WhirlpoolErrorCode(str, Enum):
    pass


class MathErrorCode(WhirlpoolErrorCode):
    MultiplicationOverflow = "MultiplicationOverflow"
    MulDivOverflow = "MulDivOverflow"
    MultiplicationShiftRightOverflow = "MultiplicationShiftRightOverflow"
    DivideByZero = "DivideByZero"


class TokenErrorCode(WhirlpoolErrorCode):
    TokenMaxExceeded = "TokenMaxExceeded"
    TokenMinSubceeded = "TokenMinSubceeded"


class SwapErrorCode(WhirlpoolErrorCode):
    InvalidSqrtPriceLimitDirection = "InvalidSqrtPriceLimitDirection"
    SqrtPriceOutOfBounds = "SqrtPriceOutOfBounds"
    ZeroTradableAmount = "ZeroTradableAmount"
    AmountOutBelowMinimum = "AmountOutBelowMinimum"
    AmountInAboveMaximum = "AmountInAboveMaximum"
    TickArrayCrossingAboveMax = "TickArrayCrossingAboveMax"
    TickArrayIndexNotInitialized = "TickArrayIndexNotInitialized"
    TickArraySequenceInvalid = "TickArraySequenceInvalid"
    SqrtPriceMaxExceeded = "SqrtPriceMaxExceeded"
    SqrtPriceMinSubceeded = "SqrtPriceMinSubceeded"
    TickArray0MustBeInitialized = "TickArray0MustBeInitialized"


class WhirlpoolError(Exception):
    def __init__(self, error_code: WhirlpoolErrorCode, message: str = None):
        if message is not None:
            super().__init__(f"{str(error_code)}: {message}")
        else:
            super().__init__(str(error_code))


class BitMath:
    @staticmethod
    def mul(n0: int, n1: int, limit: int) -> int:
        result = n0 * n1
        if BitMath.is_over_limit(result, limit):
            raise WhirlpoolError(MathErrorCode.MultiplicationOverflow)
        return result

    @staticmethod
    def mul_div(n0: int, n1: int, d: int, limit: int) -> int:
        return BitMath.mul_div_round_up_if(n0, n1, d, False, limit)

    @staticmethod
    def mul_div_round_up(n0: int, n1: int, d: int, limit: int) -> int:
        return BitMath.mul_div_round_up_if(n0, n1, d, True, limit)

    @staticmethod
    def mul_div_round_up_if(n0: int, n1: int, d: int, round_up: bool, limit: int) -> int:
        if d == 0:
            raise WhirlpoolError(MathErrorCode.DivideByZero)

        p = BitMath.mul(n0, n1, limit)
        n = p // d
        if round_up and p % d != 0:
            return n + 1
        else:
            return n

    @staticmethod
    def div_round_up(n: int, d: int) -> int:
        return BitMath.div_round_up_if(n, d, True)

    @staticmethod
    def div_round_up_if(n: int, d: int, round_up: bool) -> int:
        if d == 0:
            raise WhirlpoolError(MathErrorCode.DivideByZero)

        q = n // d
        if round_up and n % d != 0:
            return q + 1
        else:
            return q

    @staticmethod
    def is_over_limit(n0: int, limit: int) -> bool:
        ulimit_max = 2**limit - 1
        return n0 > ulimit_max




@dataclasses.dataclass(frozen=True)
class SwapResult:
    amount_a: int
    amount_b: int
    next_tick_index: int
    next_sqrt_price: int
    fee_amount: int


@dataclasses.dataclass(frozen=True)
class SwapStep:
    amount_in: int
    amount_out: int
    next_sqrt_price: int
    fee_amount: int


@dataclasses.dataclass(frozen=True)
class InitializedTick:
    tick_index: int
    tick_array_index: int
    data: Tick


class TickArraySequence:
    def __init__(
        self,
        keyed_tick_arrays: List[KeyedTickArray],
        tick_current_index: int,
        tick_spacing: int,
        direction: SwapDirection
    ):
        self.tick_spacing = tick_spacing
        self.direction = direction

        self.pubkeys = []
        self.tick_arrays = []
        self.touched = []
        for kta in keyed_tick_arrays:
            self.pubkeys.append(None if kta is None else kta.pubkey)
            self.tick_arrays.append(None if kta is None else kta.data)
            self.touched.append(False)

        if len(self.tick_arrays) == 0 or self.tick_arrays[0] is None:
            raise WhirlpoolError(SwapErrorCode.TickArray0MustBeInitialized)
        if not TickArraySequence.is_valid_tick_array_0(
                self.tick_arrays[0],
                tick_current_index,
                self.tick_spacing,
                self.direction):
            raise WhirlpoolError(SwapErrorCode.TickArraySequenceInvalid)

        self.touched[0] = True
        self.initialized_ticks = []
        for i, tick_array in enumerate(self.tick_arrays):
            if tick_array is not None:
                has_next = i+1 < len(self.tick_arrays) and self.tick_arrays[i+1] is not None
                self.initialized_ticks.extend(TickArraySequence.get_initialized_ticks(
                    tick_array,
                    i,
                    self.tick_spacing,
                    self.direction,
                    has_next,
                ))

    @staticmethod
    def is_valid_tick_array_0(
        tick_array: TickArray,
        tick_current_index: int,
        tick_spacing: int,
        direction: SwapDirection,
    ) -> bool:
        lower = tick_array.start_tick_index
        upper = tick_array.start_tick_index + tick_spacing * TICK_ARRAY_SIZE
        if direction.is_price_up:  # shifted
            lower -= tick_spacing
            upper -= tick_spacing
        return lower <= tick_current_index < upper

    @staticmethod
    def get_initialized_ticks(
        tick_array: TickArray,
        tick_array_index: int,
        tick_spacing: int,
        direction: SwapDirection,
        has_next: bool
    ) -> List[InitializedTick]:
        start_tick_index = tick_array.start_tick_index
        last_tick_index_appended = False

        if direction.is_price_up:
            last_tick_index = min(start_tick_index + tick_spacing * TICK_ARRAY_SIZE - 1, MAX_TICK_INDEX)
            ticks = list(enumerate(tick_array.ticks))
        else:
            last_tick_index = max(start_tick_index, MIN_TICK_INDEX)
            ticks = reversed(list(enumerate(tick_array.ticks)))

        initialized_ticks = []
        for i, tick in ticks:
            if tick.initialized:
                tick_index = start_tick_index + i*tick_spacing
                initialized_ticks.append(InitializedTick(tick_index, tick_array_index, tick))
                if tick_index == last_tick_index:
                    last_tick_index_appended = True

        if not has_next and not last_tick_index_appended:
            initialized_ticks.append(InitializedTick(last_tick_index, tick_array_index, Tick(False, 0, 0, 0, 0, [])))

        return initialized_ticks

    def get_next_initialized_tick_index(self, current_tick_index: int) -> int:
        for tick in self.initialized_ticks:
            if self.direction.is_price_up and tick.tick_index > current_tick_index:  # not inclusive
                return tick.tick_index
            if self.direction.is_price_down and tick.tick_index <= current_tick_index:  # inclusive
                return tick.tick_index
        raise WhirlpoolError(SwapErrorCode.TickArraySequenceInvalid)

    def get_tick(self, tick_index: int) -> Tick:
        for tick in self.initialized_ticks:
            if tick.tick_index == tick_index:
                self.touched[tick.tick_array_index] = True
                return tick.data
        # unreachable

    def get_touched_tick_array_pubkeys(self, max_swap_tick_arrays: int) -> List[PublicKey]:
        result = [self.pubkeys[0]]
        for i in range(1, max_swap_tick_arrays):
            result.append(self.pubkeys[i] if self.touched[i] else result[i-1])
        return result


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


def simulate_swap(params: SwapQuoteParams):
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
        [params.tick_array_0, params.tick_array_1, params.tick_array_2],
        whirlpool.tick_current_index,
        whirlpool.tick_spacing,
        direction,
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

    touched_tick_array_pubkeys = tick_array_sequence.get_touched_tick_array_pubkeys(MAX_SWAP_TICK_ARRAYS)

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
        tick_array_0=touched_tick_array_pubkeys[0],
        tick_array_1=touched_tick_array_pubkeys[1],
        tick_array_2=touched_tick_array_pubkeys[2],
    )


def swap_quote_with_params(
    params: SwapQuoteParams
) -> SwapQuote:
    quote = simulate_swap(params)

    if params.specified_amount.is_swap_input:
        other_amount_threshold = params.slippage_tolerance.adjust_sub(quote.estimated_amount_out)
    else:
        other_amount_threshold = params.slippage_tolerance.adjust_add(quote.estimated_amount_in)

    return SwapQuote(
        estimated_amount_in=quote.estimated_amount_in,
        estimated_amount_out=quote.estimated_amount_out,
        estimated_end_tick_index=quote.estimated_end_tick_index,
        estimated_end_sqrt_price=quote.estimated_end_sqrt_price,
        estimated_fee_amount=quote.estimated_fee_amount,
        amount=quote.amount,
        # only other_amount_threshold is modified
        other_amount_threshold=other_amount_threshold,
        sqrt_price_limit=quote.sqrt_price_limit,
        specified_amount=quote.specified_amount,
        direction=quote.direction,
        tick_array_0=quote.tick_array_0,
        tick_array_1=quote.tick_array_1,
        tick_array_2=quote.tick_array_2,
    )
