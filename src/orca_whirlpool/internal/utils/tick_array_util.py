from ..accounts.types import TickArray
from ..anchor.types import Tick
from ..constants import TICK_ARRAY_SIZE
from ..invariant import invariant
from .tick_util import TickUtil


class TickArrayUtil:
    # https://orca-so.github.io/whirlpools/classes/TickArrayUtil.html#getTickFromArray
    # https://github.com/orca-so/whirlpools/blob/7b9ec35/sdk/src/utils/public/tick-utils.ts#L155
    @staticmethod
    def get_tick_from_array(tick_array: TickArray, tick_index: int, tick_spacing) -> Tick:
        ticks_in_array = TICK_ARRAY_SIZE * tick_spacing
        invariant(
            tick_array.start_tick_index <= tick_index <= tick_array.start_tick_index + ticks_in_array,
            "tick_index must be in tick_array"
        )
        invariant(
            TickUtil.is_initializable_tick_index(tick_index, tick_spacing),
            "tick_index must be initializable"
        )
        offset = tick_index - tick_array.start_tick_index
        return tick_array.ticks[offset // tick_spacing]
