from typing import Tuple
from solders.pubkey import Pubkey
from ..types.percentage import Percentage
from ..constants import FEE_RATE_MUL_VALUE, PROTOCOL_FEE_RATE_MUL_VALUE, DEFAULT_PUBKEY
from ..anchor.types import WhirlpoolRewardInfo
from ..invariant import invariant


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
