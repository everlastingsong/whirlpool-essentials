import dataclasses
from typing import Tuple, List
from solders.pubkey import Pubkey

from ..accounts.types import TickArray, Whirlpool
from ..types.percentage import Percentage
from ..constants import FEE_RATE_MUL_VALUE, PROTOCOL_FEE_RATE_MUL_VALUE, DEFAULT_PUBKEY, MIN_TICK_INDEX
from ..anchor.types import WhirlpoolRewardInfo
from ..invariant import invariant


@dataclasses.dataclass(frozen=True)
class LiquidityDistribution:
    tick_lower_index: int
    tick_upper_index: int
    liquidity: int


class PoolUtil:
    # https://orca-so.github.io/whirlpools/classes/PoolUtil.html#isRewardInitialized
    # https://github.com/orca-so/whirlpools/blob/7b9ec35/sdk/src/utils/public/pool-utils.ts#L16
    @staticmethod
    def is_reward_initialized(reward_info: WhirlpoolRewardInfo) -> bool:
        if reward_info.mint == DEFAULT_PUBKEY or reward_info.vault == DEFAULT_PUBKEY:
            return False
        return True

    # https://orca-so.github.io/whirlpools/classes/PoolUtil.html#getFeeRate
    # https://github.com/orca-so/whirlpools/blob/7b9ec35/sdk/src/utils/public/pool-utils.ts#L38
    @staticmethod
    def get_fee_rate(fee_rate: int) -> Percentage:
        return Percentage.from_fraction(fee_rate, FEE_RATE_MUL_VALUE)

    # https://orca-so.github.io/whirlpools/classes/PoolUtil.html#getProtocolFeeRate
    # https://github.com/orca-so/whirlpools/blob/7b9ec35/sdk/src/utils/public/pool-utils.ts#L48
    @staticmethod
    def get_protocol_fee_rate(protocol_fee_rate: int) -> Percentage:
        return Percentage.from_fraction(protocol_fee_rate, PROTOCOL_FEE_RATE_MUL_VALUE)

    @staticmethod
    def order_mints(mint_x: Pubkey, mint_y: Pubkey) -> Tuple[Pubkey, Pubkey]:
        for x, y in zip(bytes(mint_x), bytes(mint_y)):
            if x < y:
                return mint_x, mint_y
            elif x > y:
                return mint_y, mint_x
        invariant(False, "mint_x and mint_y must be different")

    @staticmethod
    def get_liquidity_distribution(whirlpool: Whirlpool, tick_arrays: List[TickArray]) -> List[LiquidityDistribution]:
        tick_spacing = whirlpool.tick_spacing
        sorted_tick_arrays = sorted(tick_arrays, key=lambda ta: ta.start_tick_index)

        distribution = []
        current_lower_tick_index = MIN_TICK_INDEX
        current_liquidity = 0
        for ta in sorted_tick_arrays:
            for i, tick in enumerate(ta.ticks):
                if tick.liquidity_net == 0:
                    continue

                if current_liquidity > 0:
                    tick_index = ta.start_tick_index + i * tick_spacing
                    distribution.append(LiquidityDistribution(
                        tick_lower_index=current_lower_tick_index,
                        tick_upper_index=tick_index,
                        liquidity=current_liquidity,
                    ))
                    current_lower_tick_index = tick_index

                current_liquidity += tick.liquidity_net

        return distribution
