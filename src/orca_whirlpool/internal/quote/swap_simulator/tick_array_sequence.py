import dataclasses
from typing import List, Optional
from solders.pubkey import Pubkey
from ...invariant import invariant
from ...errors import WhirlpoolError, SwapErrorCode
from ...accounts.types import TickArray
from ...types.enums import SwapDirection, TickArrayReduction
from ...anchor.types import Tick
from ...constants import MIN_TICK_INDEX, MAX_TICK_INDEX, TICK_ARRAY_SIZE
from ...utils.swap_util import SwapUtil


@dataclasses.dataclass(frozen=True)
class InitializedTick:
    tick_index: int
    tick_array_index: int
    data: Tick


def is_consecutive_tick_arrays(
    tick_array: TickArray,
    next_tick_array: TickArray,
    tick_spacing: int,
    direction: SwapDirection
) -> bool:
    ticks_in_array = TICK_ARRAY_SIZE * tick_spacing
    if direction.is_price_up:
        expected_start_tick_index = tick_array.start_tick_index + ticks_in_array
    else:
        expected_start_tick_index = tick_array.start_tick_index - ticks_in_array
    return next_tick_array.start_tick_index == expected_start_tick_index


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


class TickArraySequence:
    def __init__(
        self,
        tick_arrays: List[Optional[TickArray]],
        tick_current_index: int,
        tick_spacing: int,
        direction: SwapDirection,
        max_swap_tick_arrays: int,
    ):
        self.tick_spacing = tick_spacing
        self.direction = direction
        self.max_swap_tick_arrays = max_swap_tick_arrays

        self.tick_arrays = []
        for i, ta in enumerate(tick_arrays[0:max_swap_tick_arrays]):
            if ta is None:
                break  # discontiguous TickArrays are not allowed.
            if i > 0 and not is_consecutive_tick_arrays(self.tick_arrays[i-1], ta, tick_spacing, direction):
                raise WhirlpoolError(SwapErrorCode.TickArraySequenceInvalid)
            self.tick_arrays.append(ta)

        if len(self.tick_arrays) == 0:
            raise WhirlpoolError(SwapErrorCode.TickArray0MustBeInitialized)

        if not SwapUtil.is_valid_tick_array_0(
                self.tick_arrays[0],
                tick_current_index,
                self.tick_spacing,
                self.direction):
            raise WhirlpoolError(SwapErrorCode.TickArraySequenceInvalid)

        self.max_touched_tick_array_index = 0
        self.initialized_ticks = []
        for tick_array_index, tick_array in enumerate(self.tick_arrays):
            has_next = tick_array_index+1 < len(self.tick_arrays)
            self.initialized_ticks.extend(get_initialized_ticks(
                tick_array,
                tick_array_index,
                self.tick_spacing,
                self.direction,
                has_next,
            ))

    def get_next_initialized_tick_index(self, current_tick_index: int) -> int:
        for tick in self.initialized_ticks:
            if self.direction.is_price_up and tick.tick_index > current_tick_index:  # not inclusive
                self.max_touched_tick_array_index = max(self.max_touched_tick_array_index, tick.tick_array_index)
                return tick.tick_index
            if self.direction.is_price_down and tick.tick_index <= current_tick_index:  # inclusive
                self.max_touched_tick_array_index = max(self.max_touched_tick_array_index, tick.tick_array_index)
                return tick.tick_index
        raise WhirlpoolError(SwapErrorCode.TickArraySequenceInvalid)

    def get_tick(self, tick_index: int) -> Tick:
        for tick in self.initialized_ticks:
            if tick.tick_index == tick_index:
                return tick.data
        invariant(False, "unreachable - tick_index is not in initialized_ticks")

    def get_tick_array_pubkeys(self, reduction: TickArrayReduction) -> List[Pubkey]:
        # reduction
        max_touched = self.max_touched_tick_array_index
        if reduction == TickArrayReduction.Aggressive:
            end = max_touched + 1
        elif reduction == TickArrayReduction.Conservative:
            end = max_touched + 1 + 1
        else:
            end = self.max_swap_tick_arrays
        result = [ta.pubkey for ta in self.tick_arrays[0:end]]

        # padding
        last = result[-1]
        while len(result) < self.max_swap_tick_arrays:
            result.append(last)
        return result
