from ..types.percentage import Percentage
from ..constants import FEE_RATE_MUL_VALUE, PROTOCOL_FEE_RATE_MUL_VALUE, DEFAULT_PUBKEY
from ..anchor.types import WhirlpoolRewardInfo


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
