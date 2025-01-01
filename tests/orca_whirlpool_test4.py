import unittest
import random
from typing import List, Any
from pyheck import snake
from solders.pubkey import Pubkey
from solders.instruction import AccountMeta
from solders.keypair import Keypair
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT as SYSVAR_RENT_PUBKEY
from spl.token.constants import TOKEN_PROGRAM_ID, TOKEN_2022_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from spl.memo.constants import MEMO_PROGRAM_ID
from anchorpy.coder.common import _sighash as sighash
from borsh_construct import Bool, U8, U16, U32, I32, U64, U128, CStruct

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
    InitializePositionBundleParams,
    InitializePositionBundleWithMetadataParams,
    DeletePositionBundleParams,
    OpenBundledPositionParams,
    CloseBundledPositionParams,
    OpenPositionWithTokenExtensionsParams,
    ClosePositionWithTokenExtensionsParams,
    TwoHopSwapParams,
    InitializeConfigExtensionParams,
    SetConfigExtensionAuthorityParams,
    SetTokenBadgeAuthorityParams,
    InitializeTokenBadgeParams,
    DeleteTokenBadgeParams,
    CollectFeesV2Params,
    CollectProtocolFeesV2Params,
    CollectRewardV2Params,
    IncreaseLiquidityV2Params,
    DecreaseLiquidityV2Params,
    InitializePoolV2Params,
    InitializeRewardV2Params,
    SetRewardEmissionsV2Params,
    SwapV2Params,
    TwoHopSwapV2Params,
)


def rand_pubkey() -> Pubkey:
    return Keypair().pubkey()


def rand_bool() -> bool:
    return random.randint(0, 1) == 0


def rand_u8() -> int:
    return random.randint(0, 2**8-1)


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
        program_id = rand_pubkey()
        position_bundle_mint = rand_pubkey()
        position_bundle_pda = PDAUtil.get_position_bundle(program_id, position_bundle_mint)
        position_bundle_token_account = rand_pubkey()
        owner = rand_pubkey()
        funder = rand_pubkey()

        result = WhirlpoolIx.initialize_position_bundle(
            program_id,
            InitializePositionBundleParams(
                position_bundle_mint=position_bundle_mint,
                position_bundle_pda=position_bundle_pda,
                position_bundle_token_account=position_bundle_token_account,
                owner=owner,
                funder=funder,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(position_bundle_pda.pubkey, keys[0])
        self.assertEqual(position_bundle_mint, keys[1])
        self.assertEqual(position_bundle_token_account, keys[2])
        self.assertEqual(owner, keys[3])
        self.assertEqual(funder, keys[4])
        self.assertEqual(TOKEN_PROGRAM_ID, keys[5])
        self.assertEqual(SYS_PROGRAM_ID, keys[6])
        self.assertEqual(SYSVAR_RENT_PUBKEY, keys[7])
        self.assertEqual(ASSOCIATED_TOKEN_PROGRAM_ID, keys[8])

        expected_data = build_ix_data("initializePositionBundle", [])
        self.assertEqual(expected_data, ix.data)

    def test_initialize_position_bundle_with_metadata_01(self):
        program_id = rand_pubkey()
        position_bundle_mint = rand_pubkey()
        position_bundle_pda = PDAUtil.get_position_bundle(program_id, position_bundle_mint)
        position_bundle_token_account = rand_pubkey()
        position_bundle_metadata_pda = PDAUtil.get_position_bundle_metadata(position_bundle_mint)
        owner = rand_pubkey()
        funder = rand_pubkey()

        result = WhirlpoolIx.initialize_position_bundle_with_metadata(
            program_id,
            InitializePositionBundleWithMetadataParams(
                position_bundle_mint=position_bundle_mint,
                position_bundle_pda=position_bundle_pda,
                position_bundle_token_account=position_bundle_token_account,
                owner=owner,
                funder=funder,
                position_bundle_metadata_pda=position_bundle_metadata_pda,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(position_bundle_pda.pubkey, keys[0])
        self.assertEqual(position_bundle_mint, keys[1])
        self.assertEqual(position_bundle_metadata_pda.pubkey, keys[2])
        self.assertEqual(position_bundle_token_account, keys[3])
        self.assertEqual(owner, keys[4])
        self.assertEqual(funder, keys[5])
        self.assertEqual(ORCA_WHIRLPOOL_NFT_UPDATE_AUTHORITY, keys[6])
        self.assertEqual(TOKEN_PROGRAM_ID, keys[7])
        self.assertEqual(SYS_PROGRAM_ID, keys[8])
        self.assertEqual(SYSVAR_RENT_PUBKEY, keys[9])
        self.assertEqual(ASSOCIATED_TOKEN_PROGRAM_ID, keys[10])
        self.assertEqual(METAPLEX_METADATA_PROGRAM_ID, keys[11])

        expected_data = build_ix_data("initializePositionBundleWithMetadata", [])
        self.assertEqual(expected_data, ix.data)

    def test_delete_position_bundle_01(self):
        program_id = rand_pubkey()
        position_bundle_mint = rand_pubkey()
        position_bundle = rand_pubkey()
        position_bundle_token_account = rand_pubkey()
        owner = rand_pubkey()
        receiver = rand_pubkey()

        result = WhirlpoolIx.delete_position_bundle(
            program_id,
            DeletePositionBundleParams(
                position_bundle=position_bundle,
                position_bundle_mint=position_bundle_mint,
                position_bundle_token_account=position_bundle_token_account,
                owner=owner,
                receiver=receiver,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(position_bundle, keys[0])
        self.assertEqual(position_bundle_mint, keys[1])
        self.assertEqual(position_bundle_token_account, keys[2])
        self.assertEqual(owner, keys[3])
        self.assertEqual(receiver, keys[4])
        self.assertEqual(TOKEN_PROGRAM_ID, keys[5])

        expected_data = build_ix_data("deletePositionBundle", [])
        self.assertEqual(expected_data, ix.data)

    def test_open_bundled_position_01(self):
        bundle_index = rand_u8()
        tick_lower_index = MIN_TICK_INDEX
        tick_upper_index = MAX_TICK_INDEX

        program_id = rand_pubkey()
        position_bundle_mint = rand_pubkey()
        position_bundle = rand_pubkey()
        bundled_position_pda = PDAUtil.get_bundled_position(program_id, position_bundle_mint, bundle_index)
        position_bundle_token_account = rand_pubkey()
        position_bundle_authority = rand_pubkey()
        whirlpool = rand_pubkey()
        funder = rand_pubkey()

        result = WhirlpoolIx.open_bundled_position(
            program_id,
            OpenBundledPositionParams(
                bundle_index=bundle_index,
                tick_lower_index=tick_lower_index,
                tick_upper_index=tick_upper_index,
                bundled_position_pda=bundled_position_pda,
                position_bundle=position_bundle,
                position_bundle_token_account=position_bundle_token_account,
                position_bundle_authority=position_bundle_authority,
                whirlpool=whirlpool,
                funder=funder,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(bundled_position_pda.pubkey, keys[0])
        self.assertEqual(position_bundle, keys[1])
        self.assertEqual(position_bundle_token_account, keys[2])
        self.assertEqual(position_bundle_authority, keys[3])
        self.assertEqual(whirlpool, keys[4])
        self.assertEqual(funder, keys[5])
        self.assertEqual(SYS_PROGRAM_ID, keys[6])
        self.assertEqual(SYSVAR_RENT_PUBKEY, keys[7])

        expected_data = build_ix_data(
            "openBundledPosition", [
                (U16, bundle_index),
                (I32, tick_lower_index),
                (I32, tick_upper_index),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_close_bundled_position_01(self):
        bundle_index = rand_u8()

        program_id = rand_pubkey()
        position_bundle = rand_pubkey()
        bundled_position = rand_pubkey()
        position_bundle_token_account = rand_pubkey()
        position_bundle_authority = rand_pubkey()
        receiver = rand_pubkey()

        result = WhirlpoolIx.close_bundled_position(
            program_id,
            CloseBundledPositionParams(
                bundle_index=bundle_index,
                bundled_position=bundled_position,
                position_bundle=position_bundle,
                position_bundle_token_account=position_bundle_token_account,
                position_bundle_authority=position_bundle_authority,
                receiver=receiver,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(bundled_position, keys[0])
        self.assertEqual(position_bundle, keys[1])
        self.assertEqual(position_bundle_token_account, keys[2])
        self.assertEqual(position_bundle_authority, keys[3])
        self.assertEqual(receiver, keys[4])

        expected_data = build_ix_data(
            "closeBundledPosition", [
                (U16, bundle_index),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_open_position_with_token_extensions_01(self):
        tick_lower_index = MIN_TICK_INDEX
        tick_upper_index = MAX_TICK_INDEX
        with_token_metadata_extension = rand_bool()

        program_id = rand_pubkey()
        funder = rand_pubkey()
        owner = rand_pubkey()
        position_mint = rand_pubkey()
        position_pda = PDAUtil.get_position(program_id, position_mint)
        position_token_account = rand_pubkey()
        whirlpool = rand_pubkey()

        result = WhirlpoolIx.open_position_with_token_extensions(
            program_id,
            OpenPositionWithTokenExtensionsParams(
                tick_lower_index=tick_lower_index,
                tick_upper_index=tick_upper_index,
                with_token_metadata_extension=with_token_metadata_extension,
                funder=funder,
                owner=owner,
                position_pda=position_pda,
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
        self.assertEqual(TOKEN_2022_PROGRAM_ID, keys[6])
        self.assertEqual(SYS_PROGRAM_ID, keys[7])
        self.assertEqual(ASSOCIATED_TOKEN_PROGRAM_ID, keys[8])
        self.assertEqual(ORCA_WHIRLPOOL_NFT_UPDATE_AUTHORITY, keys[9])

        expected_data = build_ix_data(
            "openPositionWithTokenExtensions", [
                (I32, tick_lower_index),
                (I32, tick_upper_index),
                (Bool, with_token_metadata_extension),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_close_position_with_token_extensions_01(self):
        program_id = rand_pubkey()
        position_authority = rand_pubkey()
        receiver = rand_pubkey()
        position_mint = rand_pubkey()
        position = rand_pubkey()
        position_token_account = rand_pubkey()

        result = WhirlpoolIx.close_position_with_token_extensions(
            program_id,
            ClosePositionWithTokenExtensionsParams(
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
        self.assertEqual(TOKEN_2022_PROGRAM_ID, keys[5])

        expected_data = build_ix_data("closePositionWithTokenExtensions", [])
        self.assertEqual(expected_data, ix.data)

    def test_two_hop_swap_01(self):
        amount = rand_u64()
        other_amount_threshold = rand_u64()
        amount_specified_is_input = rand_bool()
        sqrt_price_limit_one = rand_u128()
        sqrt_price_limit_two = rand_u128()
        a_to_b_one = rand_bool()
        a_to_b_two = rand_bool()

        program_id = rand_pubkey()
        token_authority = rand_pubkey()
        whirlpool_one = rand_pubkey()
        whirlpool_two = rand_pubkey()
        token_owner_account_one_a = rand_pubkey()
        token_vault_one_a = rand_pubkey()
        token_owner_account_one_b = rand_pubkey()
        token_vault_one_b = rand_pubkey()
        token_owner_account_two_a = rand_pubkey()
        token_vault_two_a = rand_pubkey()
        token_owner_account_two_b = rand_pubkey()
        token_vault_two_b = rand_pubkey()
        tick_array_one_0 = rand_pubkey()
        tick_array_one_1 = rand_pubkey()
        tick_array_one_2 = rand_pubkey()
        tick_array_two_0 = rand_pubkey()
        tick_array_two_1 = rand_pubkey()
        tick_array_two_2 = rand_pubkey()
        oracle_one = rand_pubkey()
        oracle_two = rand_pubkey()

        result = WhirlpoolIx.two_hop_swap(
            program_id,
            TwoHopSwapParams(
                amount=amount,
                other_amount_threshold=other_amount_threshold,
                amount_specified_is_input=amount_specified_is_input,
                sqrt_price_limit_one=sqrt_price_limit_one,
                sqrt_price_limit_two=sqrt_price_limit_two,
                a_to_b_one=a_to_b_one,
                a_to_b_two=a_to_b_two,
                token_authority=token_authority,
                whirlpool_one=whirlpool_one,
                whirlpool_two=whirlpool_two,
                token_owner_account_one_a=token_owner_account_one_a,
                token_vault_one_a=token_vault_one_a,
                token_owner_account_one_b=token_owner_account_one_b,
                token_vault_one_b=token_vault_one_b,
                token_owner_account_two_a=token_owner_account_two_a,
                token_vault_two_a=token_vault_two_a,
                token_owner_account_two_b=token_owner_account_two_b,
                token_vault_two_b=token_vault_two_b,
                tick_array_one_0=tick_array_one_0,
                tick_array_one_1=tick_array_one_1,
                tick_array_one_2=tick_array_one_2,
                tick_array_two_0=tick_array_two_0,
                tick_array_two_1=tick_array_two_1,
                tick_array_two_2=tick_array_two_2,
                oracle_one=oracle_one,
                oracle_two=oracle_two,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(TOKEN_PROGRAM_ID, keys[0])
        self.assertEqual(token_authority, keys[1])
        self.assertEqual(whirlpool_one, keys[2])
        self.assertEqual(whirlpool_two, keys[3])
        self.assertEqual(token_owner_account_one_a, keys[4])
        self.assertEqual(token_vault_one_a, keys[5])
        self.assertEqual(token_owner_account_one_b, keys[6])
        self.assertEqual(token_vault_one_b, keys[7])
        self.assertEqual(token_owner_account_two_a, keys[8])
        self.assertEqual(token_vault_two_a, keys[9])
        self.assertEqual(token_owner_account_two_b, keys[10])
        self.assertEqual(token_vault_two_b, keys[11])
        self.assertEqual(tick_array_one_0, keys[12])
        self.assertEqual(tick_array_one_1, keys[13])
        self.assertEqual(tick_array_one_2, keys[14])
        self.assertEqual(tick_array_two_0, keys[15])
        self.assertEqual(tick_array_two_1, keys[16])
        self.assertEqual(tick_array_two_2, keys[17])
        self.assertEqual(oracle_one, keys[18])
        self.assertEqual(oracle_two, keys[19])

        expected_data = build_ix_data(
            "twoHopSwap", [
                (U64, amount),
                (U64, other_amount_threshold),
                (Bool, amount_specified_is_input),
                (Bool, a_to_b_one),
                (Bool, a_to_b_two),
                (U128, sqrt_price_limit_one),
                (U128, sqrt_price_limit_two),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_initialize_config_extension_01(self):
        program_id = rand_pubkey()
        config = rand_pubkey()
        config_extension_pda = PDAUtil.get_whirlpools_config_extension(program_id, config)
        funder = rand_pubkey()
        fee_authority = rand_pubkey()

        result = WhirlpoolIx.initialize_config_extension(
            program_id,
            InitializeConfigExtensionParams(
                config=config,
                config_extension_pda=config_extension_pda,
                funder=funder,
                fee_authority=fee_authority,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(config, keys[0])
        self.assertEqual(config_extension_pda.pubkey, keys[1])
        self.assertEqual(funder, keys[2])
        self.assertEqual(fee_authority, keys[3])
        self.assertEqual(SYS_PROGRAM_ID, keys[4])

        expected_data = build_ix_data("initializeConfigExtension", [])
        self.assertEqual(expected_data, ix.data)

    def test_set_config_extension_authority_01(self):
        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        whirlpools_config_extension = rand_pubkey()
        config_extension_authority = rand_pubkey()
        new_config_extension_authority = rand_pubkey()

        result = WhirlpoolIx.set_config_extension_authority(
            program_id,
            SetConfigExtensionAuthorityParams(
                whirlpools_config=whirlpools_config,
                whirlpools_config_extension=whirlpools_config_extension,
                config_extension_authority=config_extension_authority,
                new_config_extension_authority=new_config_extension_authority,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(whirlpools_config_extension, keys[1])
        self.assertEqual(config_extension_authority, keys[2])
        self.assertEqual(new_config_extension_authority, keys[3])

        expected_data = build_ix_data("setConfigExtensionAuthority", [])
        self.assertEqual(expected_data, ix.data)

    def test_set_token_badge_authority_01(self):
        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        whirlpools_config_extension = rand_pubkey()
        config_extension_authority = rand_pubkey()
        new_token_badge_authority = rand_pubkey()

        result = WhirlpoolIx.set_token_badge_authority(
            program_id,
            SetTokenBadgeAuthorityParams(
                whirlpools_config=whirlpools_config,
                whirlpools_config_extension=whirlpools_config_extension,
                config_extension_authority=config_extension_authority,
                new_token_badge_authority=new_token_badge_authority,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(whirlpools_config_extension, keys[1])
        self.assertEqual(config_extension_authority, keys[2])
        self.assertEqual(new_token_badge_authority, keys[3])

        expected_data = build_ix_data("setTokenBadgeAuthority", [])
        self.assertEqual(expected_data, ix.data)

    def test_initialize_token_badge_01(self):
        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        whirlpools_config_extension = rand_pubkey()
        token_badge_authority = rand_pubkey()
        token_mint = rand_pubkey()
        token_badge_pda = PDAUtil.get_token_badge(program_id, whirlpools_config, token_mint)
        funder = rand_pubkey()

        result = WhirlpoolIx.initialize_token_badge(
            program_id,
            InitializeTokenBadgeParams(
                whirlpools_config=whirlpools_config,
                whirlpools_config_extension=whirlpools_config_extension,
                token_badge_authority=token_badge_authority,
                token_mint=token_mint,
                token_badge_pda=token_badge_pda,
                funder=funder,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(whirlpools_config_extension, keys[1])
        self.assertEqual(token_badge_authority, keys[2])
        self.assertEqual(token_mint, keys[3])
        self.assertEqual(token_badge_pda.pubkey, keys[4])
        self.assertEqual(funder, keys[5])
        self.assertEqual(SYS_PROGRAM_ID, keys[6])

        expected_data = build_ix_data("initializeTokenBadge", [])
        self.assertEqual(expected_data, ix.data)

    def test_delete_token_badge_01(self):
        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        whirlpools_config_extension = rand_pubkey()
        token_badge_authority = rand_pubkey()
        token_mint = rand_pubkey()
        token_badge = rand_pubkey()
        receiver = rand_pubkey()

        result = WhirlpoolIx.delete_token_badge(
            program_id,
            DeleteTokenBadgeParams(
                whirlpools_config=whirlpools_config,
                whirlpools_config_extension=whirlpools_config_extension,
                token_badge_authority=token_badge_authority,
                token_mint=token_mint,
                token_badge=token_badge,
                receiver=receiver,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(whirlpools_config_extension, keys[1])
        self.assertEqual(token_badge_authority, keys[2])
        self.assertEqual(token_mint, keys[3])
        self.assertEqual(token_badge, keys[4])
        self.assertEqual(receiver, keys[5])

        expected_data = build_ix_data("deleteTokenBadge", [])
        self.assertEqual(expected_data, ix.data)

    def test_collect_fees_v2_01(self):
        # without remaining accounts
        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        position_authority = rand_pubkey()
        position = rand_pubkey()
        position_token_account = rand_pubkey()
        token_mint_a = rand_pubkey()
        token_mint_b = rand_pubkey()
        token_owner_account_a = rand_pubkey()
        token_vault_a = rand_pubkey()
        token_owner_account_b = rand_pubkey()
        token_vault_b = rand_pubkey()
        token_program_a = rand_pubkey()
        token_program_b = rand_pubkey()

        result = WhirlpoolIx.collect_fees_v2(
            program_id,
            CollectFeesV2Params(
                whirlpool=whirlpool,
                position_authority=position_authority,
                position=position,
                position_token_account=position_token_account,
                token_mint_a=token_mint_a,
                token_mint_b=token_mint_b,
                token_owner_account_a=token_owner_account_a,
                token_vault_a=token_vault_a,
                token_owner_account_b=token_owner_account_b,
                token_vault_b=token_vault_b,
                token_program_a=token_program_a,
                token_program_b=token_program_b,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpool, keys[0])
        self.assertEqual(position_authority, keys[1])
        self.assertEqual(position, keys[2])
        self.assertEqual(position_token_account, keys[3])
        self.assertEqual(token_mint_a, keys[4])
        self.assertEqual(token_mint_b, keys[5])
        self.assertEqual(token_owner_account_a, keys[6])
        self.assertEqual(token_vault_a, keys[7])
        self.assertEqual(token_owner_account_b, keys[8])
        self.assertEqual(token_vault_b, keys[9])
        self.assertEqual(token_program_a, keys[10])
        self.assertEqual(token_program_b, keys[11])
        self.assertEqual(MEMO_PROGRAM_ID, keys[12])

        expected_data = build_ix_data("collectFeesV2", [
            (U8, 0)  # None
        ])
        self.assertEqual(expected_data, ix.data)

    def test_collect_fees_v2_02(self):
        # with remaining accounts
        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        position_authority = rand_pubkey()
        position = rand_pubkey()
        position_token_account = rand_pubkey()
        token_mint_a = rand_pubkey()
        token_mint_b = rand_pubkey()
        token_owner_account_a = rand_pubkey()
        token_vault_a = rand_pubkey()
        token_owner_account_b = rand_pubkey()
        token_vault_b = rand_pubkey()
        token_program_a = rand_pubkey()
        token_program_b = rand_pubkey()

        token_transfer_hook_accounts_a = [
            AccountMeta(rand_pubkey(), True, False),
            AccountMeta(rand_pubkey(), False, True),
        ]
        token_transfer_hook_accounts_b = [
            AccountMeta(rand_pubkey(), False, False),
            AccountMeta(rand_pubkey(), True, True),
        ]

        result = WhirlpoolIx.collect_fees_v2(
            program_id,
            CollectFeesV2Params(
                whirlpool=whirlpool,
                position_authority=position_authority,
                position=position,
                position_token_account=position_token_account,
                token_mint_a=token_mint_a,
                token_mint_b=token_mint_b,
                token_owner_account_a=token_owner_account_a,
                token_vault_a=token_vault_a,
                token_owner_account_b=token_owner_account_b,
                token_vault_b=token_vault_b,
                token_program_a=token_program_a,
                token_program_b=token_program_b,
                token_transfer_hook_accounts_a=token_transfer_hook_accounts_a,
                token_transfer_hook_accounts_b=token_transfer_hook_accounts_b,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpool, keys[0])
        self.assertEqual(position_authority, keys[1])
        self.assertEqual(position, keys[2])
        self.assertEqual(position_token_account, keys[3])
        self.assertEqual(token_mint_a, keys[4])
        self.assertEqual(token_mint_b, keys[5])
        self.assertEqual(token_owner_account_a, keys[6])
        self.assertEqual(token_vault_a, keys[7])
        self.assertEqual(token_owner_account_b, keys[8])
        self.assertEqual(token_vault_b, keys[9])
        self.assertEqual(token_program_a, keys[10])
        self.assertEqual(token_program_b, keys[11])
        self.assertEqual(MEMO_PROGRAM_ID, keys[12])
        # remaining
        self.assertEqual(token_transfer_hook_accounts_a[0], ix.accounts[13])
        self.assertEqual(token_transfer_hook_accounts_a[1], ix.accounts[14])
        self.assertEqual(token_transfer_hook_accounts_b[0], ix.accounts[15])
        self.assertEqual(token_transfer_hook_accounts_b[1], ix.accounts[16])
        self.assertEqual(len(ix.accounts), 17)

        expected_data = build_ix_data("collectFeesV2", [
            (U8, 1),  # Some
            (U32, 2),  # the length of slice
            (U8, 0), (U8, 2),  # TransferHookA len=2
            (U8, 1), (U8, 2),  # TransferHookB len=2
        ])
        self.assertEqual(expected_data, ix.data)

    def test_collect_protocol_fees_v2_01(self):
        # without remaining accounts
        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        whirlpool = rand_pubkey()
        collect_protocol_fees_authority = rand_pubkey()
        token_mint_a = rand_pubkey()
        token_mint_b = rand_pubkey()
        token_vault_a = rand_pubkey()
        token_vault_b = rand_pubkey()
        token_destination_a = rand_pubkey()
        token_destination_b = rand_pubkey()
        token_program_a = rand_pubkey()
        token_program_b = rand_pubkey()

        result = WhirlpoolIx.collect_protocol_fees_v2(
            program_id,
            CollectProtocolFeesV2Params(
                whirlpools_config=whirlpools_config,
                whirlpool=whirlpool,
                collect_protocol_fees_authority=collect_protocol_fees_authority,
                token_mint_a=token_mint_a,
                token_mint_b=token_mint_b,
                token_vault_a=token_vault_a,
                token_vault_b=token_vault_b,
                token_destination_a=token_destination_a,
                token_destination_b=token_destination_b,
                token_program_a=token_program_a,
                token_program_b=token_program_b,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(whirlpool, keys[1])
        self.assertEqual(collect_protocol_fees_authority, keys[2])
        self.assertEqual(token_mint_a, keys[3])
        self.assertEqual(token_mint_b, keys[4])
        self.assertEqual(token_vault_a, keys[5])
        self.assertEqual(token_vault_b, keys[6])
        self.assertEqual(token_destination_a, keys[7])
        self.assertEqual(token_destination_b, keys[8])
        self.assertEqual(token_program_a, keys[9])
        self.assertEqual(token_program_b, keys[10])
        self.assertEqual(MEMO_PROGRAM_ID, keys[11])

        expected_data = build_ix_data("collectProtocolFeesV2", [
            (U8, 0)  # None
        ])
        self.assertEqual(expected_data, ix.data)

    def test_collect_protocol_fees_v2_02(self):
        # with remaining accounts
        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        whirlpool = rand_pubkey()
        collect_protocol_fees_authority = rand_pubkey()
        token_mint_a = rand_pubkey()
        token_mint_b = rand_pubkey()
        token_vault_a = rand_pubkey()
        token_vault_b = rand_pubkey()
        token_destination_a = rand_pubkey()
        token_destination_b = rand_pubkey()
        token_program_a = rand_pubkey()
        token_program_b = rand_pubkey()

        token_transfer_hook_accounts_a = [
            AccountMeta(rand_pubkey(), True, False),
            AccountMeta(rand_pubkey(), False, True),
        ]
        token_transfer_hook_accounts_b = [
            AccountMeta(rand_pubkey(), False, False),
            AccountMeta(rand_pubkey(), True, True),
        ]

        result = WhirlpoolIx.collect_protocol_fees_v2(
            program_id,
            CollectProtocolFeesV2Params(
                whirlpools_config=whirlpools_config,
                whirlpool=whirlpool,
                collect_protocol_fees_authority=collect_protocol_fees_authority,
                token_mint_a=token_mint_a,
                token_mint_b=token_mint_b,
                token_vault_a=token_vault_a,
                token_vault_b=token_vault_b,
                token_destination_a=token_destination_a,
                token_destination_b=token_destination_b,
                token_program_a=token_program_a,
                token_program_b=token_program_b,
                token_transfer_hook_accounts_a=token_transfer_hook_accounts_a,
                token_transfer_hook_accounts_b=token_transfer_hook_accounts_b,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(whirlpool, keys[1])
        self.assertEqual(collect_protocol_fees_authority, keys[2])
        self.assertEqual(token_mint_a, keys[3])
        self.assertEqual(token_mint_b, keys[4])
        self.assertEqual(token_vault_a, keys[5])
        self.assertEqual(token_vault_b, keys[6])
        self.assertEqual(token_destination_a, keys[7])
        self.assertEqual(token_destination_b, keys[8])
        self.assertEqual(token_program_a, keys[9])
        self.assertEqual(token_program_b, keys[10])
        self.assertEqual(MEMO_PROGRAM_ID, keys[11])
        # remaining
        self.assertEqual(token_transfer_hook_accounts_a[0], ix.accounts[12])
        self.assertEqual(token_transfer_hook_accounts_a[1], ix.accounts[13])
        self.assertEqual(token_transfer_hook_accounts_b[0], ix.accounts[14])
        self.assertEqual(token_transfer_hook_accounts_b[1], ix.accounts[15])
        self.assertEqual(len(ix.accounts), 16)

        expected_data = build_ix_data("collectProtocolFeesV2", [
            (U8, 1),  # Some
            (U32, 2),  # the length of slice
            (U8, 0), (U8, 2),  # TransferHookA len=2
            (U8, 1), (U8, 2),  # TransferHookB len=2
        ])
        self.assertEqual(expected_data, ix.data)

    def test_collect_reward_v2_01(self):
        # without remaining accounts
        reward_index = 2

        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        position_authority = rand_pubkey()
        position = rand_pubkey()
        position_token_account = rand_pubkey()
        reward_owner_account = rand_pubkey()
        reward_mint = rand_pubkey()
        reward_vault = rand_pubkey()
        reward_token_program = rand_pubkey()

        result = WhirlpoolIx.collect_reward_v2(
            program_id,
            CollectRewardV2Params(
                reward_index=reward_index,
                whirlpool=whirlpool,
                position_authority=position_authority,
                position=position,
                position_token_account=position_token_account,
                reward_owner_account=reward_owner_account,
                reward_mint=reward_mint,
                reward_vault=reward_vault,
                reward_token_program=reward_token_program,
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
        self.assertEqual(reward_mint, keys[5])
        self.assertEqual(reward_vault, keys[6])
        self.assertEqual(reward_token_program, keys[7])
        self.assertEqual(MEMO_PROGRAM_ID, keys[8])

        expected_data = build_ix_data(
            "collectRewardV2", [
                (U8, reward_index),
                (U8, 0)  # None
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_collect_reward_v2_02(self):
        # without remaining accounts
        reward_index = 2

        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        position_authority = rand_pubkey()
        position = rand_pubkey()
        position_token_account = rand_pubkey()
        reward_owner_account = rand_pubkey()
        reward_mint = rand_pubkey()
        reward_vault = rand_pubkey()
        reward_token_program = rand_pubkey()

        reward_transfer_hook_accounts = [
            AccountMeta(rand_pubkey(), False, False),
            AccountMeta(rand_pubkey(), False, True),
            AccountMeta(rand_pubkey(), True, True),
        ]

        result = WhirlpoolIx.collect_reward_v2(
            program_id,
            CollectRewardV2Params(
                reward_index=reward_index,
                whirlpool=whirlpool,
                position_authority=position_authority,
                position=position,
                position_token_account=position_token_account,
                reward_owner_account=reward_owner_account,
                reward_mint=reward_mint,
                reward_vault=reward_vault,
                reward_token_program=reward_token_program,
                reward_transfer_hook_accounts=reward_transfer_hook_accounts,
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
        self.assertEqual(reward_mint, keys[5])
        self.assertEqual(reward_vault, keys[6])
        self.assertEqual(reward_token_program, keys[7])
        self.assertEqual(MEMO_PROGRAM_ID, keys[8])
        # remaining
        self.assertEqual(reward_transfer_hook_accounts[0], ix.accounts[9])
        self.assertEqual(reward_transfer_hook_accounts[1], ix.accounts[10])
        self.assertEqual(reward_transfer_hook_accounts[2], ix.accounts[11])
        self.assertEqual(len(ix.accounts), 12)

        expected_data = build_ix_data("collectRewardV2", [
            (U8, reward_index),
            (U8, 1),  # Some
            (U32, 1),  # the length of slice
            (U8, 2), (U8, 3),  # TransferHookReward len=3
        ])
        self.assertEqual(expected_data, ix.data)

    def test_increase_liquidity_v2_01(self):
        # without remaining accounts
        liquidity_amount = rand_u128()
        token_max_a = rand_u64()
        token_max_b = rand_u64()

        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        token_program_a = rand_pubkey()
        token_program_b = rand_pubkey()
        position_authority = rand_pubkey()
        position = rand_pubkey()
        position_token_account = rand_pubkey()
        token_mint_a = rand_pubkey()
        token_mint_b = rand_pubkey()
        token_owner_account_a = rand_pubkey()
        token_owner_account_b = rand_pubkey()
        token_vault_a = rand_pubkey()
        token_vault_b = rand_pubkey()
        tick_array_lower = rand_pubkey()
        tick_array_upper = rand_pubkey()

        result = WhirlpoolIx.increase_liquidity_v2(
            program_id,
            IncreaseLiquidityV2Params(
                liquidity_amount=liquidity_amount,
                token_max_a=token_max_a,
                token_max_b=token_max_b,
                whirlpool=whirlpool,
                token_program_a=token_program_a,
                token_program_b=token_program_b,
                position_authority=position_authority,
                position=position,
                position_token_account=position_token_account,
                token_mint_a=token_mint_a,
                token_mint_b=token_mint_b,
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
        self.assertEqual(token_program_a, keys[1])
        self.assertEqual(token_program_b, keys[2])
        self.assertEqual(MEMO_PROGRAM_ID, keys[3])
        self.assertEqual(position_authority, keys[4])
        self.assertEqual(position, keys[5])
        self.assertEqual(position_token_account, keys[6])
        self.assertEqual(token_mint_a, keys[7])
        self.assertEqual(token_mint_b, keys[8])
        self.assertEqual(token_owner_account_a, keys[9])
        self.assertEqual(token_owner_account_b, keys[10])
        self.assertEqual(token_vault_a, keys[11])
        self.assertEqual(token_vault_b, keys[12])
        self.assertEqual(tick_array_lower, keys[13])
        self.assertEqual(tick_array_upper, keys[14])

        expected_data = build_ix_data(
            "increaseLiquidityV2", [
                (U128, liquidity_amount),
                (U64, token_max_a),
                (U64, token_max_b),
                (U8, 0)  # None
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_increase_liquidity_v2_02(self):
        # with remaining accounts
        liquidity_amount = rand_u128()
        token_max_a = rand_u64()
        token_max_b = rand_u64()

        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        token_program_a = rand_pubkey()
        token_program_b = rand_pubkey()
        position_authority = rand_pubkey()
        position = rand_pubkey()
        position_token_account = rand_pubkey()
        token_mint_a = rand_pubkey()
        token_mint_b = rand_pubkey()
        token_owner_account_a = rand_pubkey()
        token_owner_account_b = rand_pubkey()
        token_vault_a = rand_pubkey()
        token_vault_b = rand_pubkey()
        tick_array_lower = rand_pubkey()
        tick_array_upper = rand_pubkey()

        token_transfer_hook_accounts_a = [
            AccountMeta(rand_pubkey(), True, False),
            AccountMeta(rand_pubkey(), False, True),
        ]
        token_transfer_hook_accounts_b = [
            AccountMeta(rand_pubkey(), False, False),
            AccountMeta(rand_pubkey(), True, True),
        ]

        result = WhirlpoolIx.increase_liquidity_v2(
            program_id,
            IncreaseLiquidityV2Params(
                liquidity_amount=liquidity_amount,
                token_max_a=token_max_a,
                token_max_b=token_max_b,
                whirlpool=whirlpool,
                token_program_a=token_program_a,
                token_program_b=token_program_b,
                position_authority=position_authority,
                position=position,
                position_token_account=position_token_account,
                token_mint_a=token_mint_a,
                token_mint_b=token_mint_b,
                token_owner_account_a=token_owner_account_a,
                token_owner_account_b=token_owner_account_b,
                token_vault_a=token_vault_a,
                token_vault_b=token_vault_b,
                tick_array_lower=tick_array_lower,
                tick_array_upper=tick_array_upper,
                token_transfer_hook_accounts_a=token_transfer_hook_accounts_a,
                token_transfer_hook_accounts_b=token_transfer_hook_accounts_b,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpool, keys[0])
        self.assertEqual(token_program_a, keys[1])
        self.assertEqual(token_program_b, keys[2])
        self.assertEqual(MEMO_PROGRAM_ID, keys[3])
        self.assertEqual(position_authority, keys[4])
        self.assertEqual(position, keys[5])
        self.assertEqual(position_token_account, keys[6])
        self.assertEqual(token_mint_a, keys[7])
        self.assertEqual(token_mint_b, keys[8])
        self.assertEqual(token_owner_account_a, keys[9])
        self.assertEqual(token_owner_account_b, keys[10])
        self.assertEqual(token_vault_a, keys[11])
        self.assertEqual(token_vault_b, keys[12])
        self.assertEqual(tick_array_lower, keys[13])
        self.assertEqual(tick_array_upper, keys[14])
        # remaining
        self.assertEqual(token_transfer_hook_accounts_a[0], ix.accounts[15])
        self.assertEqual(token_transfer_hook_accounts_a[1], ix.accounts[16])
        self.assertEqual(token_transfer_hook_accounts_b[0], ix.accounts[17])
        self.assertEqual(token_transfer_hook_accounts_b[1], ix.accounts[18])
        self.assertEqual(len(ix.accounts), 19)

        expected_data = build_ix_data(
            "increaseLiquidityV2", [
                (U128, liquidity_amount),
                (U64, token_max_a),
                (U64, token_max_b),
                (U8, 1),  # Some
                (U32, 2),  # the length of slice
                (U8, 0), (U8, 2),  # TransferHookA len=2
                (U8, 1), (U8, 2),  # TransferHookB len=2
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_decrease_liquidity_v2_01(self):
        # without remaining accounts
        liquidity_amount = rand_u128()
        token_min_a = rand_u64()
        token_min_b = rand_u64()

        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        token_program_a = rand_pubkey()
        token_program_b = rand_pubkey()
        position_authority = rand_pubkey()
        position = rand_pubkey()
        position_token_account = rand_pubkey()
        token_mint_a = rand_pubkey()
        token_mint_b = rand_pubkey()
        token_owner_account_a = rand_pubkey()
        token_owner_account_b = rand_pubkey()
        token_vault_a = rand_pubkey()
        token_vault_b = rand_pubkey()
        tick_array_lower = rand_pubkey()
        tick_array_upper = rand_pubkey()

        result = WhirlpoolIx.decrease_liquidity_v2(
            program_id,
            DecreaseLiquidityV2Params(
                liquidity_amount=liquidity_amount,
                token_min_a=token_min_a,
                token_min_b=token_min_b,
                whirlpool=whirlpool,
                token_program_a=token_program_a,
                token_program_b=token_program_b,
                position_authority=position_authority,
                position=position,
                position_token_account=position_token_account,
                token_mint_a=token_mint_a,
                token_mint_b=token_mint_b,
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
        self.assertEqual(token_program_a, keys[1])
        self.assertEqual(token_program_b, keys[2])
        self.assertEqual(MEMO_PROGRAM_ID, keys[3])
        self.assertEqual(position_authority, keys[4])
        self.assertEqual(position, keys[5])
        self.assertEqual(position_token_account, keys[6])
        self.assertEqual(token_mint_a, keys[7])
        self.assertEqual(token_mint_b, keys[8])
        self.assertEqual(token_owner_account_a, keys[9])
        self.assertEqual(token_owner_account_b, keys[10])
        self.assertEqual(token_vault_a, keys[11])
        self.assertEqual(token_vault_b, keys[12])
        self.assertEqual(tick_array_lower, keys[13])
        self.assertEqual(tick_array_upper, keys[14])

        expected_data = build_ix_data(
            "decreaseLiquidityV2", [
                (U128, liquidity_amount),
                (U64, token_min_a),
                (U64, token_min_b),
                (U8, 0)  # None
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_decrease_liquidity_v2_02(self):
        # with remaining accounts
        liquidity_amount = rand_u128()
        token_min_a = rand_u64()
        token_min_b = rand_u64()

        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        token_program_a = rand_pubkey()
        token_program_b = rand_pubkey()
        position_authority = rand_pubkey()
        position = rand_pubkey()
        position_token_account = rand_pubkey()
        token_mint_a = rand_pubkey()
        token_mint_b = rand_pubkey()
        token_owner_account_a = rand_pubkey()
        token_owner_account_b = rand_pubkey()
        token_vault_a = rand_pubkey()
        token_vault_b = rand_pubkey()
        tick_array_lower = rand_pubkey()
        tick_array_upper = rand_pubkey()

        token_transfer_hook_accounts_a = [
            AccountMeta(rand_pubkey(), True, False),
            AccountMeta(rand_pubkey(), False, True),
        ]
        token_transfer_hook_accounts_b = [
            AccountMeta(rand_pubkey(), False, False),
            AccountMeta(rand_pubkey(), True, True),
        ]

        result = WhirlpoolIx.decrease_liquidity_v2(
            program_id,
            DecreaseLiquidityV2Params(
                liquidity_amount=liquidity_amount,
                token_min_a=token_min_a,
                token_min_b=token_min_b,
                whirlpool=whirlpool,
                token_program_a=token_program_a,
                token_program_b=token_program_b,
                position_authority=position_authority,
                position=position,
                position_token_account=position_token_account,
                token_mint_a=token_mint_a,
                token_mint_b=token_mint_b,
                token_owner_account_a=token_owner_account_a,
                token_owner_account_b=token_owner_account_b,
                token_vault_a=token_vault_a,
                token_vault_b=token_vault_b,
                tick_array_lower=tick_array_lower,
                tick_array_upper=tick_array_upper,
                token_transfer_hook_accounts_a=token_transfer_hook_accounts_a,
                token_transfer_hook_accounts_b=token_transfer_hook_accounts_b,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpool, keys[0])
        self.assertEqual(token_program_a, keys[1])
        self.assertEqual(token_program_b, keys[2])
        self.assertEqual(MEMO_PROGRAM_ID, keys[3])
        self.assertEqual(position_authority, keys[4])
        self.assertEqual(position, keys[5])
        self.assertEqual(position_token_account, keys[6])
        self.assertEqual(token_mint_a, keys[7])
        self.assertEqual(token_mint_b, keys[8])
        self.assertEqual(token_owner_account_a, keys[9])
        self.assertEqual(token_owner_account_b, keys[10])
        self.assertEqual(token_vault_a, keys[11])
        self.assertEqual(token_vault_b, keys[12])
        self.assertEqual(tick_array_lower, keys[13])
        self.assertEqual(tick_array_upper, keys[14])
        # remaining
        self.assertEqual(token_transfer_hook_accounts_a[0], ix.accounts[15])
        self.assertEqual(token_transfer_hook_accounts_a[1], ix.accounts[16])
        self.assertEqual(token_transfer_hook_accounts_b[0], ix.accounts[17])
        self.assertEqual(token_transfer_hook_accounts_b[1], ix.accounts[18])
        self.assertEqual(len(ix.accounts), 19)

        expected_data = build_ix_data(
            "decreaseLiquidityV2", [
                (U128, liquidity_amount),
                (U64, token_min_a),
                (U64, token_min_b),
                (U8, 1),  # Some
                (U32, 2),  # the length of slice
                (U8, 0), (U8, 2),  # TransferHookA len=2
                (U8, 1), (U8, 2),  # TransferHookB len=2
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_initialize_pool_v2_01(self):
        tick_spacing = random.randint(1, 255)
        initial_sqrt_price = rand_u128()

        program_id = rand_pubkey()
        whirlpools_config = rand_pubkey()
        token_mint_a = rand_pubkey()
        token_mint_b = rand_pubkey()
        token_badge_a = rand_pubkey()
        token_badge_b = rand_pubkey()
        funder = rand_pubkey()
        whirlpool_pda = PDAUtil.get_whirlpool(
            program_id,
            whirlpools_config,
            token_mint_a,
            token_mint_b,
            tick_spacing,
        )
        token_vault_a = rand_pubkey()
        token_vault_b = rand_pubkey()
        fee_tier = rand_pubkey()
        token_program_a = rand_pubkey()
        token_program_b = rand_pubkey()

        result = WhirlpoolIx.initialize_pool_v2(
            program_id,
            InitializePoolV2Params(
                tick_spacing=tick_spacing,
                initial_sqrt_price=initial_sqrt_price,
                whirlpools_config=whirlpools_config,
                token_mint_a=token_mint_a,
                token_mint_b=token_mint_b,
                token_badge_a=token_badge_a,
                token_badge_b=token_badge_b,
                funder=funder,
                whirlpool_pda=whirlpool_pda,
                token_vault_a=token_vault_a,
                token_vault_b=token_vault_b,
                fee_tier=fee_tier,
                token_program_a=token_program_a,
                token_program_b=token_program_b,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(whirlpools_config, keys[0])
        self.assertEqual(token_mint_a, keys[1])
        self.assertEqual(token_mint_b, keys[2])
        self.assertEqual(token_badge_a, keys[3])
        self.assertEqual(token_badge_b, keys[4])
        self.assertEqual(funder, keys[5])
        self.assertEqual(whirlpool_pda.pubkey, keys[6])
        self.assertEqual(token_vault_a, keys[7])
        self.assertEqual(token_vault_b, keys[8])
        self.assertEqual(fee_tier, keys[9])
        self.assertEqual(token_program_a, keys[10])
        self.assertEqual(token_program_b, keys[11])
        self.assertEqual(SYS_PROGRAM_ID, keys[12])
        self.assertEqual(SYSVAR_RENT_PUBKEY, keys[13])

        expected_data = build_ix_data("initializePoolV2", [
            (U16, tick_spacing),
            (U128, initial_sqrt_price),
        ])
        self.assertEqual(expected_data, ix.data)

    def test_initialize_reward_v2_01(self):
        reward_index = 2

        program_id = rand_pubkey()
        reward_authority = rand_pubkey()
        funder = rand_pubkey()
        whirlpool = rand_pubkey()
        reward_mint = rand_pubkey()
        reward_token_badge = rand_pubkey()
        reward_vault = rand_pubkey()
        reward_token_program = rand_pubkey()

        result = WhirlpoolIx.initialize_reward_v2(
            program_id,
            InitializeRewardV2Params(
                reward_index=reward_index,
                reward_authority=reward_authority,
                funder=funder,
                whirlpool=whirlpool,
                reward_mint=reward_mint,
                reward_token_badge=reward_token_badge,
                reward_vault=reward_vault,
                reward_token_program=reward_token_program,
            )
        )
        ix = result.instructions[0]

        self.assertEqual(program_id, ix.program_id)

        keys = list(map(lambda k: k.pubkey, ix.accounts))
        self.assertEqual(reward_authority, keys[0])
        self.assertEqual(funder, keys[1])
        self.assertEqual(whirlpool, keys[2])
        self.assertEqual(reward_mint, keys[3])
        self.assertEqual(reward_token_badge, keys[4])
        self.assertEqual(reward_vault, keys[5])
        self.assertEqual(reward_token_program, keys[6])
        self.assertEqual(SYS_PROGRAM_ID, keys[7])
        self.assertEqual(SYSVAR_RENT_PUBKEY, keys[8])

        expected_data = build_ix_data(
            "initializeRewardV2", [
                (U8, reward_index),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_set_reward_emissions_v2_01(self):
        reward_index = 2
        emissions_per_second_x64 = rand_u128()

        program_id = rand_pubkey()
        whirlpool = rand_pubkey()
        reward_authority = rand_pubkey()
        reward_vault = rand_pubkey()

        result = WhirlpoolIx.set_reward_emissions_v2(
            program_id,
            SetRewardEmissionsV2Params(
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
            "setRewardEmissionsV2", [
                (U8, reward_index),
                (U128, emissions_per_second_x64),
            ]
        )
        self.assertEqual(expected_data, ix.data)

    def test_swap_v2_01(self):
        # must: check remaining accounts info and accounts
        self.assertTrue(False, "not implemented")

    def test_two_hop_swap_v2_01(self):
        # must: check remaining accounts info and accounts
        self.assertTrue(False, "not implemented")


if __name__ == "__main__":
    unittest.main()
