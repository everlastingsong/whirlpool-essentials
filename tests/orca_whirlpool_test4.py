import unittest
import random
from typing import List, Any
from pyheck import snake
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT as SYSVAR_RENT_PUBKEY
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from anchorpy.coder.common import _sighash as sighash
from borsh_construct import Bool, U8, U16, I32, U64, U128, CStruct

from orca_whirlpool.internal.utils.pda_util import PDAUtil
from orca_whirlpool.internal.constants import (
    MIN_TICK_INDEX,
    MAX_TICK_INDEX,
    METAPLEX_METADATA_PROGRAM_ID,
    ORCA_WHIRLPOOL_NFT_UPDATE_AUTHORITY
)
from orca_whirlpool.internal.instruction.whirlpoolix import (
    WhirlpoolIx,
    SwapParams,
    OpenPositionParams,
    OpenPositionWithMetadataParams,
    IncreaseLiquidityParams,
    DecreaseLiquidityParams,
    UpdateFeesAndRewardsParams,
    CollectFeesParams,
    CollectRewardParams,
    ClosePositionParams,
    CollectProtocolFeesParams,
    InitializeConfigParams,
    InitializeFeeTierParams,
    InitializePoolParams,
    InitializeRewardParams,
    InitializeTickArrayParams,
    SetCollectProtocolFeesAuthorityParams,
    SetDefaultFeeRateParams,
    SetDefaultProtocolFeeRateParams,
    SetFeeAuthorityParams,
    SetFeeRateParams,
    SetProtocolFeeRateParams,
    SetRewardAuthorityBySuperAuthorityParams,
    SetRewardAuthorityParams,
    SetRewardEmissionsParams,
    SetRewardEmissionsSuperAuthorityParams,
)


def rand_pubkey() -> Pubkey:
    return Keypair().pubkey()


def rand_bool() -> bool:
    return random.randint(0, 1) == 0


def rand_u64() -> int:
    return random.randint(0, 2**64-1)


def rand_u128() -> int:
    return random.randint(0, 2**128-1)


def build_ix_data(ix_name: str, ix_data: List[Any]) -> bytes:
    ix_name_snake = snake(ix_name)
    ixsighash = sighash(ix_name_snake)

    data = [(U8[8], ixsighash)] + ix_data
    cstruct = CStruct(*[f'field{i}' / d[0] for i, d in enumerate(data)])

    encoded = cstruct.build(dict([[f'field{i}', d[1]] for i, d in enumerate(data)]))
    return encoded


class WhirlpoolIxTestCase(unittest.TestCase):
    def test_swap_01(self):
        amount = rand_u64()
        other_amount_threshold = rand_u64()
        sqrt_price_limit = rand_u128()
        amount_specified_is_input = rand_bool()
        a_to_b = rand_bool()

        program_id = rand_pubkey()
        token_authority = rand_pubkey()
        whirlpool = rand_pubkey()
        token_owner_account_a = rand_pubkey()
        token_vault_a = rand_pubkey()
        token_owner_account_b = rand_pubkey()
        token_vault_b = rand_pubkey()
        tick_array_0 = rand_pubkey()
        tick_array_1 = rand_pubkey()
        tick_array_2 = rand_pubkey()
        oracle = rand_pubkey()

        result = WhirlpoolIx.swap(
            program_id,
            SwapParams(
                amount=amount,
                other_amount_threshold=other_amount_threshold,
                sqrt_price_limit=sqrt_price_limit,
                amount_specified_is_input=amount_specified_is_input,
                a_to_b=a_to_b,
                token_authority=token_authority,
                whirlpool=whirlpool,
                token_owner_account_a=token_owner_account_a,
                token_vault_a=token_vault_a,
                token_owner_account_b=token_owner_account_b,
                token_vault_b=token_vault_b,
                tick_array_0=tick_array_0,
                tick_array_1=tick_array_1,
                tick_array_2=tick_array_2,
                oracle=oracle
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(TOKEN_PROGRAM_ID, keys[0])
        self.assertEqual(token_authority, keys[1])
        self.assertEqual(whirlpool, keys[2])
        self.assertEqual(token_owner_account_a, keys[3])
        self.assertEqual(token_vault_a, keys[4])
        self.assertEqual(token_owner_account_b, keys[5])
        self.assertEqual(token_vault_b, keys[6])
        self.assertEqual(tick_array_0, keys[7])
        self.assertEqual(tick_array_1, keys[8])
        self.assertEqual(tick_array_2, keys[9])
        self.assertEqual(oracle, keys[10])

        expected_data = build_ix_data(
            "swap", [
                (U64, amount),
                (U64, other_amount_threshold),
                (U128, sqrt_price_limit),
                (Bool, amount_specified_is_input),
                (Bool, a_to_b),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_open_position_01(self):
        tick_lower_index = MIN_TICK_INDEX
        tick_upper_index = MAX_TICK_INDEX

        program_id = rand_pubkey()
        funder = rand_pubkey()
        owner = rand_pubkey()
        position_mint = rand_pubkey()
        position_pda = PDAUtil.get_position(program_id, position_mint)
        position_token_account = rand_pubkey()
        whirlpool = rand_pubkey()

        result = WhirlpoolIx.open_position(
            program_id,
            OpenPositionParams(
                tick_lower_index=tick_lower_index,
                tick_upper_index=tick_upper_index,
                position_pda=position_pda,
                funder=funder,
                owner=owner,
                position_mint=position_mint,
                position_token_account=position_token_account,
                whirlpool=whirlpool,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(funder, keys[0])
        self.assertEqual(owner, keys[1])
        self.assertEqual(position_pda.pubkey, keys[2])
        self.assertEqual(position_mint, keys[3])
        self.assertEqual(position_token_account, keys[4])
        self.assertEqual(whirlpool, keys[5])
        self.assertEqual(TOKEN_PROGRAM_ID, keys[6])
        self.assertEqual(SYS_PROGRAM_ID, keys[7])
        self.assertEqual(SYSVAR_RENT_PUBKEY, keys[8])
        self.assertEqual(ASSOCIATED_TOKEN_PROGRAM_ID, keys[9])

        expected_data = build_ix_data(
            "openPosition", [
                (U8, position_pda.bump),
                (I32, tick_lower_index),
                (I32, tick_upper_index),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_open_position_with_metadata_01(self):
        tick_lower_index = MIN_TICK_INDEX
        tick_upper_index = MAX_TICK_INDEX

        program_id = rand_pubkey()
        funder = rand_pubkey()
        owner = rand_pubkey()
        position_mint = rand_pubkey()
        position_pda = PDAUtil.get_position(program_id, position_mint)
        position_token_account = rand_pubkey()
        metadata_pda = PDAUtil.get_position_metadata(position_mint)
        whirlpool = rand_pubkey()

        result = WhirlpoolIx.open_position_with_metadata(
            program_id,
            OpenPositionWithMetadataParams(
                tick_lower_index=tick_lower_index,
                tick_upper_index=tick_upper_index,
                position_pda=position_pda,
                funder=funder,
                owner=owner,
                position_mint=position_mint,
                metadata_pda=metadata_pda,
                position_token_account=position_token_account,
                whirlpool=whirlpool,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(funder, keys[0])
        self.assertEqual(owner, keys[1])
        self.assertEqual(position_pda.pubkey, keys[2])
        self.assertEqual(position_mint, keys[3])
        self.assertEqual(metadata_pda.pubkey, keys[4])
        self.assertEqual(position_token_account, keys[5])
        self.assertEqual(whirlpool, keys[6])
        self.assertEqual(TOKEN_PROGRAM_ID, keys[7])
        self.assertEqual(SYS_PROGRAM_ID, keys[8])
        self.assertEqual(SYSVAR_RENT_PUBKEY, keys[9])
        self.assertEqual(ASSOCIATED_TOKEN_PROGRAM_ID, keys[10])
        self.assertEqual(METAPLEX_METADATA_PROGRAM_ID, keys[11])
        self.assertEqual(ORCA_WHIRLPOOL_NFT_UPDATE_AUTHORITY, keys[12])

        expected_data = build_ix_data(
            "openPositionWithMetadata", [
                (U8, position_pda.bump),
                (U8, metadata_pda.bump),
                (I32, tick_lower_index),
                (I32, tick_upper_index),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_increase_liquidity_01(self):
        liquidity_amount = rand_u128()
        token_max_a = rand_u64()
        token_max_b = rand_u64()

        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        position_authority = rand_pubkey()
        position = rand_pubkey()
        position_token_account = rand_pubkey()
        token_owner_account_a = rand_pubkey()
        token_owner_account_b = rand_pubkey()
        token_vault_a = rand_pubkey()
        token_vault_b = rand_pubkey()
        tick_array_lower = rand_pubkey()
        tick_array_upper = rand_pubkey()

        result = WhirlpoolIx.increase_liquidity(
            program_id,
            IncreaseLiquidityParams(
                liquidity_amount=liquidity_amount,
                token_max_a=token_max_a,
                token_max_b=token_max_b,
                whirlpool=whirlpool,
                position_authority=position_authority,
                position=position,
                position_token_account=position_token_account,
                token_owner_account_a=token_owner_account_a,
                token_owner_account_b=token_owner_account_b,
                token_vault_a=token_vault_a,
                token_vault_b=token_vault_b,
                tick_array_lower=tick_array_lower,
                tick_array_upper=tick_array_upper,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpool, keys[0])
        self.assertEqual(TOKEN_PROGRAM_ID, keys[1])
        self.assertEqual(position_authority, keys[2])
        self.assertEqual(position, keys[3])
        self.assertEqual(position_token_account, keys[4])
        self.assertEqual(token_owner_account_a, keys[5])
        self.assertEqual(token_owner_account_b, keys[6])
        self.assertEqual(token_vault_a, keys[7])
        self.assertEqual(token_vault_b, keys[8])
        self.assertEqual(tick_array_lower, keys[9])
        self.assertEqual(tick_array_upper, keys[10])

        expected_data = build_ix_data(
            "increaseLiquidity", [
                (U128, liquidity_amount),
                (U64, token_max_a),
                (U64, token_max_b),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_decrease_liquidity_01(self):
        liquidity_amount = rand_u128()
        token_min_a = rand_u64()
        token_min_b = rand_u64()

        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        position_authority = rand_pubkey()
        position = rand_pubkey()
        position_token_account = rand_pubkey()
        token_owner_account_a = rand_pubkey()
        token_owner_account_b = rand_pubkey()
        token_vault_a = rand_pubkey()
        token_vault_b = rand_pubkey()
        tick_array_lower = rand_pubkey()
        tick_array_upper = rand_pubkey()

        result = WhirlpoolIx.decrease_liquidity(
            program_id,
            DecreaseLiquidityParams(
                liquidity_amount=liquidity_amount,
                token_min_a=token_min_a,
                token_min_b=token_min_b,
                whirlpool=whirlpool,
                position_authority=position_authority,
                position=position,
                position_token_account=position_token_account,
                token_owner_account_a=token_owner_account_a,
                token_owner_account_b=token_owner_account_b,
                token_vault_a=token_vault_a,
                token_vault_b=token_vault_b,
                tick_array_lower=tick_array_lower,
                tick_array_upper=tick_array_upper,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpool, keys[0])
        self.assertEqual(TOKEN_PROGRAM_ID, keys[1])
        self.assertEqual(position_authority, keys[2])
        self.assertEqual(position, keys[3])
        self.assertEqual(position_token_account, keys[4])
        self.assertEqual(token_owner_account_a, keys[5])
        self.assertEqual(token_owner_account_b, keys[6])
        self.assertEqual(token_vault_a, keys[7])
        self.assertEqual(token_vault_b, keys[8])
        self.assertEqual(tick_array_lower, keys[9])
        self.assertEqual(tick_array_upper, keys[10])

        expected_data = build_ix_data(
            "decreaseLiquidity", [
                (U128, liquidity_amount),
                (U64, token_min_a),
                (U64, token_min_b),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_update_fees_and_rewards_01(self):
        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        position = rand_pubkey()
        tick_array_lower = rand_pubkey()
        tick_array_upper = rand_pubkey()

        result = WhirlpoolIx.update_fees_and_rewards(
            program_id,
            UpdateFeesAndRewardsParams(
                whirlpool=whirlpool,
                position=position,
                tick_array_lower=tick_array_lower,
                tick_array_upper=tick_array_upper,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpool, keys[0])
        self.assertEqual(position, keys[1])
        self.assertEqual(tick_array_lower, keys[2])
        self.assertEqual(tick_array_upper, keys[3])

        expected_data = build_ix_data("updateFeesAndRewards", [])
        self.assertEqual(expected_data, ix.data)

    def test_collect_fees_01(self):
        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        position_authority = rand_pubkey()
        position = rand_pubkey()
        position_token_account = rand_pubkey()
        token_owner_account_a = rand_pubkey()
        token_vault_a = rand_pubkey()
        token_owner_account_b = rand_pubkey()
        token_vault_b = rand_pubkey()

        result = WhirlpoolIx.collect_fees(
            program_id,
            CollectFeesParams(
                whirlpool=whirlpool,
                position_authority=position_authority,
                position=position,
                position_token_account=position_token_account,
                token_owner_account_a=token_owner_account_a,
                token_vault_a=token_vault_a,
                token_owner_account_b=token_owner_account_b,
                token_vault_b=token_vault_b,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpool, keys[0])
        self.assertEqual(position_authority, keys[1])
        self.assertEqual(position, keys[2])
        self.assertEqual(position_token_account, keys[3])
        self.assertEqual(token_owner_account_a, keys[4])
        self.assertEqual(token_vault_a, keys[5])
        self.assertEqual(token_owner_account_b, keys[6])
        self.assertEqual(token_vault_b, keys[7])
        self.assertEqual(TOKEN_PROGRAM_ID, keys[8])

        expected_data = build_ix_data("collectFees", [])
        self.assertEqual(expected_data, ix.data)

    def test_collect_reward_01(self):
        reward_index = 2

        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        position_authority = rand_pubkey()
        position = rand_pubkey()
        position_token_account = rand_pubkey()
        reward_owner_account = rand_pubkey()
        reward_vault = rand_pubkey()

        result = WhirlpoolIx.collect_reward(
            program_id,
            CollectRewardParams(
                reward_index=reward_index,
                whirlpool=whirlpool,
                position_authority=position_authority,
                position=position,
                position_token_account=position_token_account,
                reward_owner_account=reward_owner_account,
                reward_vault=reward_vault,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpool, keys[0])
        self.assertEqual(position_authority, keys[1])
        self.assertEqual(position, keys[2])
        self.assertEqual(position_token_account, keys[3])
        self.assertEqual(reward_owner_account, keys[4])
        self.assertEqual(reward_vault, keys[5])
        self.assertEqual(TOKEN_PROGRAM_ID, keys[6])

        expected_data = build_ix_data(
            "collectReward", [
                (U8, reward_index),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_collect_protocol_fees_01(self):
        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        whirlpool = rand_pubkey()
        collect_protocol_fees_authority = rand_pubkey()
        token_vault_a = rand_pubkey()
        token_vault_b = rand_pubkey()
        token_destination_a = rand_pubkey()
        token_destination_b = rand_pubkey()

        result = WhirlpoolIx.collect_protocol_fees(
            program_id,
            CollectProtocolFeesParams(
                whirlpools_config=whirlpools_config,
                whirlpool=whirlpool,
                collect_protocol_fees_authority=collect_protocol_fees_authority,
                token_vault_a=token_vault_a,
                token_vault_b=token_vault_b,
                token_destination_a=token_destination_a,
                token_destination_b=token_destination_b,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(whirlpool, keys[1])
        self.assertEqual(collect_protocol_fees_authority, keys[2])
        self.assertEqual(token_vault_a, keys[3])
        self.assertEqual(token_vault_b, keys[4])
        self.assertEqual(token_destination_a, keys[5])
        self.assertEqual(token_destination_b, keys[6])
        self.assertEqual(TOKEN_PROGRAM_ID, keys[7])

        expected_data = build_ix_data("collectProtocolFees", [])
        self.assertEqual(expected_data, ix.data)

    def test_close_position_01(self):
        program_id = rand_pubkey()
        position_authority = rand_pubkey()
        receiver = rand_pubkey()
        position = rand_pubkey()
        position_mint = rand_pubkey()
        position_token_account = rand_pubkey()

        result = WhirlpoolIx.close_position(
            program_id,
            ClosePositionParams(
                position_authority=position_authority,
                receiver=receiver,
                position=position,
                position_mint=position_mint,
                position_token_account=position_token_account,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(position_authority, keys[0])
        self.assertEqual(receiver, keys[1])
        self.assertEqual(position, keys[2])
        self.assertEqual(position_mint, keys[3])
        self.assertEqual(position_token_account, keys[4])
        self.assertEqual(TOKEN_PROGRAM_ID, keys[5])

        expected_data = build_ix_data("closePosition", [])
        self.assertEqual(expected_data, ix.data)

    def test_initialize_config_01(self):
        fee_authority = rand_pubkey()
        collect_protocol_fees_authority = rand_pubkey()
        reward_emissions_super_authority = rand_pubkey()
        default_protocol_fee_rate = random.randint(1, 2500)

        program_id = rand_pubkey()
        config = rand_pubkey()
        funder = rand_pubkey()

        result = WhirlpoolIx.initialize_config(
            program_id,
            InitializeConfigParams(
                fee_authority=fee_authority,
                collect_protocol_fees_authority=collect_protocol_fees_authority,
                reward_emissions_super_authority=reward_emissions_super_authority,
                default_protocol_fee_rate=default_protocol_fee_rate,
                config=config,
                funder=funder,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(config, keys[0])
        self.assertEqual(funder, keys[1])
        self.assertEqual(SYS_PROGRAM_ID, keys[2])

        expected_data = build_ix_data(
            "initializeConfig", [
                (U8[32], bytes(fee_authority)),
                (U8[32], bytes(collect_protocol_fees_authority)),
                (U8[32], bytes(reward_emissions_super_authority)),
                (U16, default_protocol_fee_rate),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_initialize_fee_tier_01(self):
        tick_spacing = random.randint(1, 255)
        default_fee_rate = random.randint(1, 10000)

        program_id = rand_pubkey()
        config = rand_pubkey()
        fee_tier = rand_pubkey()
        funder = rand_pubkey()
        fee_authority = rand_pubkey()

        result = WhirlpoolIx.initialize_fee_tier(
            program_id,
            InitializeFeeTierParams(
                tick_spacing=tick_spacing,
                default_fee_rate=default_fee_rate,
                config=config,
                fee_tier=fee_tier,
                funder=funder,
                fee_authority=fee_authority,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(config, keys[0])
        self.assertEqual(fee_tier, keys[1])
        self.assertEqual(funder, keys[2])
        self.assertEqual(fee_authority, keys[3])
        self.assertEqual(SYS_PROGRAM_ID, keys[4])

        expected_data = build_ix_data(
            "initializeFeeTier", [
                (U16, tick_spacing),
                (U16, default_fee_rate),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_initialize_pool_01(self):
        tick_spacing = random.randint(1, 255)
        initial_sqrt_price = rand_u128()

        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        token_mint_a = rand_pubkey()
        token_mint_b = rand_pubkey()
        funder = rand_pubkey()
        whirlpool_pda = PDAUtil.get_whirlpool(program_id, whirlpools_config, token_mint_a, token_mint_b, tick_spacing)
        token_vault_a = rand_pubkey()
        token_vault_b = rand_pubkey()
        fee_tier = rand_pubkey()

        result = WhirlpoolIx.initialize_pool(
            program_id,
            InitializePoolParams(
                tick_spacing=tick_spacing,
                initial_sqrt_price=initial_sqrt_price,
                whirlpools_config=whirlpools_config,
                token_mint_a=token_mint_a,
                token_mint_b=token_mint_b,
                funder=funder,
                whirlpool_pda=whirlpool_pda,
                token_vault_a=token_vault_a,
                token_vault_b=token_vault_b,
                fee_tier=fee_tier,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(token_mint_a, keys[1])
        self.assertEqual(token_mint_b, keys[2])
        self.assertEqual(funder, keys[3])
        self.assertEqual(whirlpool_pda.pubkey, keys[4])
        self.assertEqual(token_vault_a, keys[5])
        self.assertEqual(token_vault_b, keys[6])
        self.assertEqual(fee_tier, keys[7])
        self.assertEqual(TOKEN_PROGRAM_ID, keys[8])
        self.assertEqual(SYS_PROGRAM_ID, keys[9])
        self.assertEqual(SYSVAR_RENT_PUBKEY, keys[10])

        expected_data = build_ix_data(
            "initializePool", [
                (U8, whirlpool_pda.bump),
                (U16, tick_spacing),
                (U128, initial_sqrt_price),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_initialize_reward_01(self):
        reward_index = 2

        program_id = rand_pubkey()
        reward_authority = rand_pubkey()
        funder = rand_pubkey()
        whirlpool = rand_pubkey()
        reward_mint = rand_pubkey()
        reward_vault = rand_pubkey()

        result = WhirlpoolIx.initialize_reward(
            program_id,
            InitializeRewardParams(
                reward_index=reward_index,
                reward_authority=reward_authority,
                funder=funder,
                whirlpool=whirlpool,
                reward_mint=reward_mint,
                reward_vault=reward_vault,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(reward_authority, keys[0])
        self.assertEqual(funder, keys[1])
        self.assertEqual(whirlpool, keys[2])
        self.assertEqual(reward_mint, keys[3])
        self.assertEqual(reward_vault, keys[4])
        self.assertEqual(TOKEN_PROGRAM_ID, keys[5])
        self.assertEqual(SYS_PROGRAM_ID, keys[6])
        self.assertEqual(SYSVAR_RENT_PUBKEY, keys[7])

        expected_data = build_ix_data(
            "initializeReward", [
                (U8, reward_index),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_initialize_tick_array_01(self):
        start_tick_index = random.randint(MIN_TICK_INDEX, MAX_TICK_INDEX)

        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        funder = rand_pubkey()
        tick_array = rand_pubkey()

        result = WhirlpoolIx.initialize_tick_array(
            program_id,
            InitializeTickArrayParams(
                start_tick_index=start_tick_index,
                whirlpool=whirlpool,
                funder=funder,
                tick_array=tick_array,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpool, keys[0])
        self.assertEqual(funder, keys[1])
        self.assertEqual(tick_array, keys[2])
        self.assertEqual(SYS_PROGRAM_ID, keys[3])

        expected_data = build_ix_data(
            "initializeTickArray", [
                (I32, start_tick_index),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_set_collect_protocol_fees_authority_01(self):
        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        collect_protocol_fees_authority = rand_pubkey()
        new_collect_protocol_fees_authority = rand_pubkey()

        result = WhirlpoolIx.set_collect_protocol_fees_authority(
            program_id,
            SetCollectProtocolFeesAuthorityParams(
                whirlpools_config=whirlpools_config,
                collect_protocol_fees_authority=collect_protocol_fees_authority,
                new_collect_protocol_fees_authority=new_collect_protocol_fees_authority,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(collect_protocol_fees_authority, keys[1])
        self.assertEqual(new_collect_protocol_fees_authority, keys[2])

        expected_data = build_ix_data("setCollectProtocolFeesAuthority", [])
        self.assertEqual(expected_data, ix.data)

    def test_set_default_fee_rate_01(self):
        default_fee_rate = random.randint(1, 10000)

        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        fee_tier = rand_pubkey()
        fee_authority = rand_pubkey()

        result = WhirlpoolIx.set_default_fee_rate(
            program_id,
            SetDefaultFeeRateParams(
                default_fee_rate=default_fee_rate,
                whirlpools_config=whirlpools_config,
                fee_tier=fee_tier,
                fee_authority=fee_authority,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(fee_tier, keys[1])
        self.assertEqual(fee_authority, keys[2])

        expected_data = build_ix_data(
            "setDefaultFeeRate", [
                (U16, default_fee_rate),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_set_default_protocol_fee_rate_01(self):
        default_protocol_fee_rate = random.randint(1, 2500)

        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        fee_authority = rand_pubkey()

        result = WhirlpoolIx.set_default_protocol_fee_rate(
            program_id,
            SetDefaultProtocolFeeRateParams(
                default_protocol_fee_rate=default_protocol_fee_rate,
                whirlpools_config=whirlpools_config,
                fee_authority=fee_authority,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(fee_authority, keys[1])

        expected_data = build_ix_data(
            "setDefaultProtocolFeeRate", [
                (U16, default_protocol_fee_rate),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_set_fee_authority_01(self):
        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        fee_authority = rand_pubkey()
        new_fee_authority = rand_pubkey()

        result = WhirlpoolIx.set_fee_authority(
            program_id,
            SetFeeAuthorityParams(
                whirlpools_config=whirlpools_config,
                fee_authority=fee_authority,
                new_fee_authority=new_fee_authority,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(fee_authority, keys[1])
        self.assertEqual(new_fee_authority, keys[2])

        expected_data = build_ix_data("setFeeAuthority", [])
        self.assertEqual(expected_data, ix.data)

    def test_set_fee_rate_01(self):
        fee_rate = random.randint(1, 10000)

        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        whirlpool = rand_pubkey()
        fee_authority = rand_pubkey()

        result = WhirlpoolIx.set_fee_rate(
            program_id,
            SetFeeRateParams(
                fee_rate=fee_rate,
                whirlpools_config=whirlpools_config,
                whirlpool=whirlpool,
                fee_authority=fee_authority,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(whirlpool, keys[1])
        self.assertEqual(fee_authority, keys[2])

        expected_data = build_ix_data(
            "setFeeRate", [
                (U16, fee_rate),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_set_protocol_fee_rate_01(self):
        protocol_fee_rate = random.randint(1, 2500)

        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        whirlpool = rand_pubkey()
        fee_authority = rand_pubkey()

        result = WhirlpoolIx.set_protocol_fee_rate(
            program_id,
            SetProtocolFeeRateParams(
                protocol_fee_rate=protocol_fee_rate,
                whirlpools_config=whirlpools_config,
                whirlpool=whirlpool,
                fee_authority=fee_authority,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(whirlpool, keys[1])
        self.assertEqual(fee_authority, keys[2])

        expected_data = build_ix_data(
            "setProtocolFeeRate", [
                (U16, protocol_fee_rate),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_set_reward_authority_01(self):
        reward_index = 2

        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        reward_authority = rand_pubkey()
        new_reward_authority = rand_pubkey()

        result = WhirlpoolIx.set_reward_authority(
            program_id,
            SetRewardAuthorityParams(
                reward_index=reward_index,
                whirlpool=whirlpool,
                reward_authority=reward_authority,
                new_reward_authority=new_reward_authority,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpool, keys[0])
        self.assertEqual(reward_authority, keys[1])
        self.assertEqual(new_reward_authority, keys[2])

        expected_data = build_ix_data(
            "setRewardAuthority", [
                (U8, reward_index),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_set_reward_authority_by_super_authority_01(self):
        reward_index = 2

        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        whirlpool = rand_pubkey()
        reward_emissions_super_authority = rand_pubkey()
        new_reward_authority = rand_pubkey()

        result = WhirlpoolIx.set_reward_authority_by_super_authority(
            program_id,
            SetRewardAuthorityBySuperAuthorityParams(
                reward_index=reward_index,
                whirlpools_config=whirlpools_config,
                whirlpool=whirlpool,
                reward_emissions_super_authority=reward_emissions_super_authority,
                new_reward_authority=new_reward_authority,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(whirlpool, keys[1])
        self.assertEqual(reward_emissions_super_authority, keys[2])
        self.assertEqual(new_reward_authority, keys[3])

        expected_data = build_ix_data(
            "setRewardAuthorityBySuperAuthority", [
                (U8, reward_index),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_set_reward_emissions_01(self):
        reward_index = 2
        emissions_per_second_x64 = rand_u128()

        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        reward_authority = rand_pubkey()
        reward_vault = rand_pubkey()

        result = WhirlpoolIx.set_reward_emissions(
            program_id,
            SetRewardEmissionsParams(
                reward_index=reward_index,
                emissions_per_second_x64=emissions_per_second_x64,
                whirlpool=whirlpool,
                reward_authority=reward_authority,
                reward_vault=reward_vault,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpool, keys[0])
        self.assertEqual(reward_authority, keys[1])
        self.assertEqual(reward_vault, keys[2])

        expected_data = build_ix_data(
            "setRewardEmissions", [
                (U8, reward_index),
                (U128, emissions_per_second_x64),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_set_reward_emissions_super_authority_01(self):
        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        reward_emissions_super_authority = rand_pubkey()
        new_reward_emissions_super_authority = rand_pubkey()

        result = WhirlpoolIx.set_reward_emissions_super_authority(
            program_id,
            SetRewardEmissionsSuperAuthorityParams(
                whirlpools_config=whirlpools_config,
                reward_emissions_super_authority=reward_emissions_super_authority,
                new_reward_emissions_super_authority=new_reward_emissions_super_authority,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(reward_emissions_super_authority, keys[1])
        self.assertEqual(new_reward_emissions_super_authority, keys[2])

        expected_data = build_ix_data("setRewardEmissionsSuperAuthority", [])
        self.assertEqual(expected_data, ix.data)

    def test_initialize_position_bundle_01(self):
        self.assertTrue(False, "not implemented")

    def test_initialize_position_bundle_with_metadata_01(self):
        self.assertTrue(False, "not implemented")

    def test_delete_position_bundle_01(self):
        self.assertTrue(False, "not implemented")

    def test_open_bundled_position_01(self):
        self.assertTrue(False, "not implemented")

    def test_close_bundled_position_01(self):
        self.assertTrue(False, "not implemented")

    def test_open_position_with_token_extensions_01(self):
        self.assertTrue(False, "not implemented")

    def test_close_position_with_token_extensions_01(self):
        self.assertTrue(False, "not implemented")

    def test_two_hop_swap_01(self):
        self.assertTrue(False, "not implemented")

    def test_initialize_config_extension_01(self):
        self.assertTrue(False, "not implemented")

    def test_set_config_extension_authority_01(self):
        self.assertTrue(False, "not implemented")

    def test_set_token_badge_authority_01(self):
        self.assertTrue(False, "not implemented")

    def test_initialize_token_badge_01(self):
        self.assertTrue(False, "not implemented")

    def test_delete_token_badge_01(self):
        self.assertTrue(False, "not implemented")


if __name__ == "__main__":
    unittest.main()
