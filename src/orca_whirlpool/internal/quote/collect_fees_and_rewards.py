# https://github.com/orca-so/whirlpools/blob/main/sdk/src/quotes/public/decrease-liquidity-quote.ts

import dataclasses
from typing import List, Optional
from ..accounts.types import Whirlpool, Position
from ..anchor.types import Tick
from ..types.enums import PositionStatus
from ..invariant import invariant
from ..utils.pool_util import PoolUtil
from ..utils.position_util import PositionUtil
from ..utils.q64_fixed_point_math import Q64FixedPointMath
from ..constants import NUM_REWARDS


@dataclasses.dataclass(frozen=True)
class CollectFeesQuoteParams:
    whirlpool: Whirlpool
    position: Position
    tick_lower: Tick
    tick_upper: Tick


@dataclasses.dataclass(frozen=True)
class CollectFeesQuote:
    fee_a: int
    fee_b: int


@dataclasses.dataclass(frozen=True)
class CollectRewardsQuoteParams:
    whirlpool: Whirlpool
    position: Position
    tick_lower: Tick
    tick_upper: Tick
    latest_block_timestamp: int = None


@dataclasses.dataclass(frozen=True)
class CollectRewardsQuote:
    rewards: List[Optional[int]]


def u128_checked_mul_div_or_zero(u128a: int, u128b: int, u128c: int) -> int:
    u128max = 2**128 - 1
    invariant(0 <= u128a <= u128max, "u128a must be u128 integer")
    invariant(0 <= u128b <= u128max, "u128b must be u128 integer")
    invariant(0 <= u128c <= u128max, "u128c must be u128 integer")
    if u128c == 0:
        return 0
    if u128a * u128b > u128max:
        return 0
    return u128a * u128b // u128c


def u128_modular_subtraction(u128a: int, u128b: int) -> int:
    modulo = 2**128
    invariant(0 <= u128a < modulo, "u128a must be u128 integer")
    invariant(0 <= u128b < modulo, "u128b must be u128 integer")
    return (u128a + (modulo - u128b)) % modulo


def collect_fees_quote(
    params: CollectFeesQuoteParams
) -> CollectFeesQuote:
    position = params.position
    status = PositionUtil.get_position_status(
        params.whirlpool.tick_current_index,
        position.tick_lower_index,
        position.tick_upper_index
    )

    global_a = params.whirlpool.fee_growth_global_a
    global_b = params.whirlpool.fee_growth_global_b
    lower_a = params.tick_lower.fee_growth_outside_a
    lower_b = params.tick_lower.fee_growth_outside_b
    upper_a = params.tick_upper.fee_growth_outside_a
    upper_b = params.tick_upper.fee_growth_outside_b
    invariant(lower_a <= global_a, "tick_lower.fee_growth_outside_a <= whirlpool.fee_growth_global_a")
    invariant(upper_a <= global_a, "tick_upper.fee_growth_outside_a <= whirlpool.fee_growth_global_a")
    invariant(lower_b <= global_b, "tick_lower.fee_growth_outside_b <= whirlpool.fee_growth_global_b")
    invariant(upper_b <= global_b, "tick_upper.fee_growth_outside_b <= whirlpool.fee_growth_global_b")

    below_a = lower_a
    below_b = lower_b
    if status == PositionStatus.PriceIsBelowRange:
        below_a = global_a - lower_a
        below_b = global_b - lower_b
    above_a = upper_a
    above_b = upper_b
    if status == PositionStatus.PriceIsAboveRange:
        above_a = global_a - upper_a
        above_b = global_b - upper_b

    inside_a = u128_modular_subtraction(u128_modular_subtraction(global_a, below_a), above_a)
    inside_b = u128_modular_subtraction(u128_modular_subtraction(global_b, below_b), above_b)
    delta_a = u128_modular_subtraction(inside_a, position.fee_growth_checkpoint_a)
    delta_b = u128_modular_subtraction(inside_b, position.fee_growth_checkpoint_b)

    fee_owed_a_delta = Q64FixedPointMath.x64int_to_int(delta_a * position.liquidity)
    fee_owed_b_delta = Q64FixedPointMath.x64int_to_int(delta_b * position.liquidity)

    return CollectFeesQuote(
        fee_a=position.fee_owed_a + fee_owed_a_delta,
        fee_b=position.fee_owed_b + fee_owed_b_delta,
    )


def collect_rewards_quote(
    params: CollectRewardsQuoteParams
) -> CollectRewardsQuote:
    reward_infos = params.whirlpool.reward_infos
    invariant(len(reward_infos) == NUM_REWARDS, "len(reward_infos) == NUM_REWARDS")

    position = params.position
    status = PositionUtil.get_position_status(
        params.whirlpool.tick_current_index,
        position.tick_lower_index,
        position.tick_upper_index
    )

    # Unix time (second) in u64
    timestamp_delta = 0
    if params.latest_block_timestamp is not None:
        timestamp_delta = max(0, params.latest_block_timestamp - params.whirlpool.reward_last_updated_timestamp)

    rewards: List[Optional[int]] = []
    for i, reward_info in enumerate(reward_infos):
        if not PoolUtil.is_reward_initialized(reward_info):
            rewards.append(None)
            continue

        global_ri_delta = u128_checked_mul_div_or_zero(
            reward_info.emissions_per_second_x64,
            timestamp_delta,
            params.whirlpool.liquidity
        )

        global_ri = reward_info.growth_global_x64 + global_ri_delta
        lower_ri = params.tick_lower.reward_growths_outside[i]
        upper_ri = params.tick_upper.reward_growths_outside[i]
        invariant(lower_ri <= global_ri, "tick_lower.reward_growth_outside <= reward_info.growth_global")
        invariant(upper_ri <= global_ri, "tick_upper.reward_growth_outside <= reward_info.growth_global")

        below_ri = lower_ri
        if status == PositionStatus.PriceIsBelowRange:
            below_ri = global_ri - lower_ri
        above_ri = upper_ri
        if status == PositionStatus.PriceIsAboveRange:
            above_ri = global_ri - above_ri

        inside_ri = u128_modular_subtraction(u128_modular_subtraction(global_ri, below_ri), above_ri)
        delta_ri = u128_modular_subtraction(inside_ri, position.reward_infos[i].growth_inside_checkpoint)

        reward_owed_ri_delta = Q64FixedPointMath.x64int_to_int(delta_ri * position.liquidity)

        rewards.append(position.reward_infos[i].amount_owed + reward_owed_ri_delta)

    return CollectRewardsQuote(rewards)
