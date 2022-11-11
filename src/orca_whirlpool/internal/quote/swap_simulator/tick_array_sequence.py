import dataclasses
from typing import List
from solana.publickey import PublicKey
from ...errors import WhirlpoolError, SwapErrorCode
from ...types.types import KeyedTickArray
from ...types.enums import SwapDirection
from ...anchor.accounts import TickArray
from ...anchor.types import Tick
from ...constants import MIN_TICK_INDEX, MAX_TICK_INDEX, TICK_ARRAY_SIZE


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
