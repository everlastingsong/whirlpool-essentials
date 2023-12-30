from typing import List
from solders.pubkey import Pubkey
from ..constants import U64_MAX, MIN_SQRT_PRICE, MAX_SQRT_PRICE, MAX_SWAP_TICK_ARRAYS, TICK_ARRAY_SIZE
from ..types.enums import SwapDirection, SpecifiedAmount
from ..invariant import InvaliantFailedError
from ..accounts.types import TickArray
from .tick_util import TickUtil
from .pda_util import PDAUtil


class SwapUtil:
    # https://orca-so.github.io/whirlpools/classes/SwapUtils.html#getDefaultSqrtPriceLimit
    # https://github.com/orca-so/whirlpools/blob/2df89bb/sdk/src/utils/public/swap-utils.ts#L28
    @staticmethod
    def get_default_sqrt_price_limit(direction: SwapDirection) -> int:
        return MIN_SQRT_PRICE if direction.is_price_down else MAX_SQRT_PRICE

    # https://orca-so.github.io/whirlpools/classes/SwapUtils.html#getDefaultOtherAmountThreshold
    # https://github.com/orca-so/whirlpools/blob/7b9ec35/sdk/src/utils/public/swap-utils.ts#L37
    @staticmethod
    def get_default_other_amount_threshold(specified_amount: SpecifiedAmount) -> int:
        return 0 if specified_amount.is_swap_input else U64_MAX

    # https://orca-so.github.io/whirlpools/classes/SwapUtils.html#getTickArrayPublicKeys
    # https://github.com/orca-so/whirlpools/blob/2df89bb/sdk/src/utils/public/swap-utils.ts#L75
    @staticmethod
    def get_tick_array_pubkeys(
        tick_current_index: int,
        tick_spacing: int,
        direction: SwapDirection,
        program_id: Pubkey,
        whirlpool_pubkey: Pubkey,
    ) -> List[Pubkey]:
        # https://github.com/orca-so/whirlpools/blob/7b9ec351e2048c5504ffc8894c0ec5a9e78dc113/programs/whirlpool/src/state/tick.rs#L299
        shifted = 0 if direction.is_price_down else tick_spacing

        offset = 0
        pubkeys = []
        for i in range(MAX_SWAP_TICK_ARRAYS):
            try:
                start_tick_index = TickUtil.get_start_tick_index(tick_current_index + shifted, tick_spacing, offset)
            except InvaliantFailedError:
                return pubkeys

            tick_array_pubkey = PDAUtil.get_tick_array(program_id, whirlpool_pubkey, start_tick_index).pubkey
            pubkeys.append(tick_array_pubkey)
            offset += -1 if direction.is_price_down else +1
        return pubkeys

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
