import dataclasses
from typing import List

from solders.instruction import Instruction as TransactionInstruction
from solders.pubkey import Pubkey
from solders.keypair import Keypair
# from solders.sysvar import RENT
# from solders.system_program import ID as SYS_PROGRAM_ID
# from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from ..anchor import instructions
from ..anchor import types
from ..constants import METAPLEX_METADATA_PROGRAM_ID, ORCA_WHIRLPOOL_NFT_UPDATE_AUTHORITY
from ..types.types import PDA
from ..transaction.types import Instruction


def to_instruction(
    instructions: List[TransactionInstruction],
    cleanup_instructions: List[TransactionInstruction] = None,
    signers: List[Keypair] = None
) -> Instruction:
    cleanup_instructions = [] if cleanup_instructions is None else cleanup_instructions
    signers = [] if signers is None else signers
    return Instruction(
        instructions=instructions,
        cleanup_instructions=cleanup_instructions,
        signers=signers,
    )


@dataclasses.dataclass(frozen=True)
class SwapParams:
    amount: int
    other_amount_threshold: int
    sqrt_price_limit: int
    amount_specified_is_input: bool
    a_to_b: bool
    token_authority: Pubkey
    whirlpool: Pubkey
    token_owner_account_a: Pubkey
    token_vault_a: Pubkey
    token_owner_account_b: Pubkey
    token_vault_b: Pubkey
    tick_array_0: Pubkey
    tick_array_1: Pubkey
    tick_array_2: Pubkey
    oracle: Pubkey


@dataclasses.dataclass(frozen=True)
class OpenPositionParams:
    tick_lower_index: int
    tick_upper_index: int
    position_pda: PDA
    funder: Pubkey
    owner: Pubkey
    position_mint: Pubkey
    position_token_account: Pubkey
    whirlpool: Pubkey


@dataclasses.dataclass(frozen=True)
class OpenPositionWithMetadataParams:
    tick_lower_index: int
    tick_upper_index: int
    position_pda: PDA
    metadata_pda: PDA
    funder: Pubkey
    owner: Pubkey
    position_mint: Pubkey
    position_token_account: Pubkey
    whirlpool: Pubkey


@dataclasses.dataclass(frozen=True)
class IncreaseLiquidityParams:
    liquidity_amount: int
    token_max_a: int
    token_max_b: int
    whirlpool: Pubkey
    position_authority: Pubkey
    position: Pubkey
    position_token_account: Pubkey
    token_owner_account_a: Pubkey
    token_owner_account_b: Pubkey
    token_vault_a: Pubkey
    token_vault_b: Pubkey
    tick_array_lower: Pubkey
    tick_array_upper: Pubkey


@dataclasses.dataclass(frozen=True)
class DecreaseLiquidityParams:
    liquidity_amount: int
    token_min_a: int
    token_min_b: int
    whirlpool: Pubkey
    position_authority: Pubkey
    position: Pubkey
    position_token_account: Pubkey
    token_owner_account_a: Pubkey
    token_owner_account_b: Pubkey
    token_vault_a: Pubkey
    token_vault_b: Pubkey
    tick_array_lower: Pubkey
    tick_array_upper: Pubkey


@dataclasses.dataclass(frozen=True)
class UpdateFeesAndRewardsParams:
    whirlpool: Pubkey
    position: Pubkey
    tick_array_lower: Pubkey
    tick_array_upper: Pubkey


@dataclasses.dataclass(frozen=True)
class CollectFeesParams:
    whirlpool: Pubkey
    position_authority: Pubkey
    position: Pubkey
    position_token_account: Pubkey
    token_owner_account_a: Pubkey
    token_vault_a: Pubkey
    token_owner_account_b: Pubkey
    token_vault_b: Pubkey


@dataclasses.dataclass(frozen=True)
class CollectRewardParams:
    reward_index: int
    whirlpool: Pubkey
    position_authority: Pubkey
    position: Pubkey
    position_token_account: Pubkey
    reward_owner_account: Pubkey
    reward_vault: Pubkey


@dataclasses.dataclass(frozen=True)
class ClosePositionParams:
    position_authority: Pubkey
    receiver: Pubkey
    position: Pubkey
    position_mint: Pubkey
    position_token_account: Pubkey


@dataclasses.dataclass(frozen=True)
class InitializeTickArrayParams:
    start_tick_index: int
    whirlpool: Pubkey
    funder: Pubkey
    tick_array: Pubkey


@dataclasses.dataclass(frozen=True)
class InitializeConfigParams:
    default_protocol_fee_rate: int
    fee_authority: Pubkey
    collect_protocol_fees_authority: Pubkey
    reward_emissions_super_authority: Pubkey
    config: Pubkey
    funder: Pubkey


@dataclasses.dataclass(frozen=True)
class InitializeFeeTierParams:
    tick_spacing: int
    default_fee_rate: int
    config: Pubkey
    fee_tier: Pubkey
    funder: Pubkey
    fee_authority: Pubkey


@dataclasses.dataclass(frozen=True)
class InitializePoolParams:
    tick_spacing: int
    initial_sqrt_price: int
    whirlpool_pda: PDA
    whirlpools_config: Pubkey
    token_mint_a: Pubkey
    token_mint_b: Pubkey
    funder: Pubkey
    token_vault_a: Pubkey
    token_vault_b: Pubkey
    fee_tier: Pubkey


@dataclasses.dataclass(frozen=True)
class InitializeRewardParams:
    reward_index: int
    reward_authority: Pubkey
    funder: Pubkey
    whirlpool: Pubkey
    reward_mint: Pubkey
    reward_vault: Pubkey


@dataclasses.dataclass(frozen=True)
class CollectProtocolFeesParams:
    whirlpools_config: Pubkey
    whirlpool: Pubkey
    collect_protocol_fees_authority: Pubkey
    token_vault_a: Pubkey
    token_vault_b: Pubkey
    token_destination_a: Pubkey
    token_destination_b: Pubkey


@dataclasses.dataclass(frozen=True)
class SetCollectProtocolFeesAuthorityParams:
    whirlpools_config: Pubkey
    collect_protocol_fees_authority: Pubkey
    new_collect_protocol_fees_authority: Pubkey


@dataclasses.dataclass(frozen=True)
class SetDefaultFeeRateParams:
    default_fee_rate: int
    whirlpools_config: Pubkey
    fee_tier: Pubkey
    fee_authority: Pubkey


@dataclasses.dataclass(frozen=True)
class SetDefaultProtocolFeeRateParams:
    default_protocol_fee_rate: int
    whirlpools_config: Pubkey
    fee_authority: Pubkey


@dataclasses.dataclass(frozen=True)
class SetFeeAuthorityParams:
    whirlpools_config: Pubkey
    fee_authority: Pubkey
    new_fee_authority: Pubkey


@dataclasses.dataclass(frozen=True)
class SetFeeRateParams:
    fee_rate: int
    whirlpools_config: Pubkey
    whirlpool: Pubkey
    fee_authority: Pubkey


@dataclasses.dataclass(frozen=True)
class SetProtocolFeeRateParams:
    protocol_fee_rate: int
    whirlpools_config: Pubkey
    whirlpool: Pubkey
    fee_authority: Pubkey


@dataclasses.dataclass(frozen=True)
class SetRewardAuthorityParams:
    reward_index: int
    whirlpool: Pubkey
    reward_authority: Pubkey
    new_reward_authority: Pubkey


@dataclasses.dataclass(frozen=True)
class SetRewardAuthorityBySuperAuthorityParams:
    reward_index: int
    whirlpools_config: Pubkey
    whirlpool: Pubkey
    reward_emissions_super_authority: Pubkey
    new_reward_authority: Pubkey


@dataclasses.dataclass(frozen=True)
class SetRewardEmissionsParams:
    reward_index: int
    emissions_per_second_x64: int
    whirlpool: Pubkey
    reward_authority: Pubkey
    reward_vault: Pubkey


@dataclasses.dataclass(frozen=True)
class SetRewardEmissionsSuperAuthorityParams:
    whirlpools_config: Pubkey
    reward_emissions_super_authority: Pubkey
    new_reward_emissions_super_authority: Pubkey


@dataclasses.dataclass(frozen=True)
class InitializePositionBundleParams:
    owner: Pubkey
    position_bundle_pda: PDA
    position_bundle_mint: Pubkey
    position_bundle_token_account: Pubkey
    funder: Pubkey


@dataclasses.dataclass(frozen=True)
class InitializePositionBundleWithMetadataParams:
    owner: Pubkey
    position_bundle_pda: PDA
    position_bundle_mint: Pubkey
    position_bundle_token_account: Pubkey
    funder: Pubkey
    position_bundle_metadata_pda: PDA


@dataclasses.dataclass(frozen=True)
class DeletePositionBundleParams:
    owner: Pubkey
    position_bundle: Pubkey
    position_bundle_mint: Pubkey
    position_bundle_token_account: Pubkey
    receiver: Pubkey


@dataclasses.dataclass(frozen=True)
class OpenBundledPositionParams:
    bundle_index: int
    tick_lower_index: int
    tick_upper_index: int
    whirlpool: Pubkey
    bundled_position_pda: PDA
    position_bundle: Pubkey
    position_bundle_token_account: Pubkey
    position_bundle_authority: Pubkey
    funder: Pubkey


@dataclasses.dataclass(frozen=True)
class CloseBundledPositionParams:
    bundle_index: int
    bundled_position: Pubkey
    position_bundle: Pubkey
    position_bundle_token_account: Pubkey
    position_bundle_authority: Pubkey
    receiver: Pubkey


class WhirlpoolIx:
    @staticmethod
    def swap(program_id: Pubkey, params: SwapParams):
        ix = instructions.swap(
            instructions.SwapArgs(
                amount=params.amount,
                other_amount_threshold=params.other_amount_threshold,
                sqrt_price_limit=params.sqrt_price_limit,
                amount_specified_is_input=params.amount_specified_is_input,
                a_to_b=params.a_to_b,
            ),
            instructions.SwapAccounts(
                # token_program=TOKEN_PROGRAM_ID,
                token_authority=params.token_authority,
                whirlpool=params.whirlpool,
                token_owner_account_a=params.token_owner_account_a,
                token_vault_a=params.token_vault_a,
                token_owner_account_b=params.token_owner_account_b,
                token_vault_b=params.token_vault_b,
                tick_array0=params.tick_array_0,
                tick_array1=params.tick_array_1,
                tick_array2=params.tick_array_2,
                oracle=params.oracle,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def open_position(program_id: Pubkey, params: OpenPositionParams):
        ix = instructions.open_position(
            instructions.OpenPositionArgs(
                tick_lower_index=params.tick_lower_index,
                tick_upper_index=params.tick_upper_index,
                bumps=types.open_position_bumps.OpenPositionBumps(params.position_pda.bump),
            ),
            instructions.OpenPositionAccounts(
                funder=params.funder,
                owner=params.owner,
                position=params.position_pda.pubkey,
                position_mint=params.position_mint,
                position_token_account=params.position_token_account,
                whirlpool=params.whirlpool,
                # token_program=TOKEN_PROGRAM_ID,
                # system_program=SYS_PROGRAM_ID,
                # rent=RENT,
                # associated_token_program=ASSOCIATED_TOKEN_PROGRAM_ID,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def open_position_with_metadata(program_id: Pubkey, params: OpenPositionWithMetadataParams):
        ix = instructions.open_position_with_metadata(
            instructions.OpenPositionWithMetadataArgs(
                tick_lower_index=params.tick_lower_index,
                tick_upper_index=params.tick_upper_index,
                bumps=types.open_position_with_metadata_bumps.OpenPositionWithMetadataBumps(
                    position_bump=params.position_pda.bump,
                    metadata_bump=params.metadata_pda.bump,
                ),
            ),
            instructions.OpenPositionWithMetadataAccounts(
                funder=params.funder,
                owner=params.owner,
                position=params.position_pda.pubkey,
                position_mint=params.position_mint,
                position_metadata_account=params.metadata_pda.pubkey,
                position_token_account=params.position_token_account,
                whirlpool=params.whirlpool,
                # token_program=TOKEN_PROGRAM_ID,
                # system_program=SYS_PROGRAM_ID,
                # rent=RENT,
                # associated_token_program=ASSOCIATED_TOKEN_PROGRAM_ID,
                metadata_program=METAPLEX_METADATA_PROGRAM_ID,
                metadata_update_auth=ORCA_WHIRLPOOL_NFT_UPDATE_AUTHORITY,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def increase_liquidity(program_id: Pubkey, params: IncreaseLiquidityParams):
        ix = instructions.increase_liquidity(
            instructions.IncreaseLiquidityArgs(
                liquidity_amount=params.liquidity_amount,
                token_max_a=params.token_max_a,
                token_max_b=params.token_max_b,
            ),
            instructions.IncreaseLiquidityAccounts(
                whirlpool=params.whirlpool,
                # token_program=TOKEN_PROGRAM_ID,
                position_authority=params.position_authority,
                position=params.position,
                position_token_account=params.position_token_account,
                token_owner_account_a=params.token_owner_account_a,
                token_owner_account_b=params.token_owner_account_b,
                token_vault_a=params.token_vault_a,
                token_vault_b=params.token_vault_b,
                tick_array_lower=params.tick_array_lower,
                tick_array_upper=params.tick_array_upper,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def decrease_liquidity(program_id: Pubkey, params: DecreaseLiquidityParams):
        ix = instructions.decrease_liquidity(
            instructions.DecreaseLiquidityArgs(
                liquidity_amount=params.liquidity_amount,
                token_min_a=params.token_min_a,
                token_min_b=params.token_min_b,
            ),
            instructions.DecreaseLiquidityAccounts(
                whirlpool=params.whirlpool,
                # token_program=TOKEN_PROGRAM_ID,
                position_authority=params.position_authority,
                position=params.position,
                position_token_account=params.position_token_account,
                token_owner_account_a=params.token_owner_account_a,
                token_owner_account_b=params.token_owner_account_b,
                token_vault_a=params.token_vault_a,
                token_vault_b=params.token_vault_b,
                tick_array_lower=params.tick_array_lower,
                tick_array_upper=params.tick_array_upper,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def update_fees_and_rewards(program_id: Pubkey, params: UpdateFeesAndRewardsParams):
        ix = instructions.update_fees_and_rewards(
            instructions.UpdateFeesAndRewardsAccounts(
                whirlpool=params.whirlpool,
                position=params.position,
                tick_array_lower=params.tick_array_lower,
                tick_array_upper=params.tick_array_upper,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def collect_fees(program_id: Pubkey, params: CollectFeesParams):
        ix = instructions.collect_fees(
            instructions.CollectFeesAccounts(
                whirlpool=params.whirlpool,
                position_authority=params.position_authority,
                position=params.position,
                position_token_account=params.position_token_account,
                token_owner_account_a=params.token_owner_account_a,
                token_vault_a=params.token_vault_a,
                token_owner_account_b=params.token_owner_account_b,
                token_vault_b=params.token_vault_b,
                # token_program=TOKEN_PROGRAM_ID,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def collect_reward(program_id: Pubkey, params: CollectRewardParams):
        ix = instructions.collect_reward(
            instructions.CollectRewardArgs(
                reward_index=params.reward_index,
            ),
            instructions.CollectRewardAccounts(
                whirlpool=params.whirlpool,
                position_authority=params.position_authority,
                position=params.position,
                position_token_account=params.position_token_account,
                reward_owner_account=params.reward_owner_account,
                reward_vault=params.reward_vault,
                # token_program=TOKEN_PROGRAM_ID,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def close_position(program_id: Pubkey, params: ClosePositionParams):
        ix = instructions.close_position(
            instructions.ClosePositionAccounts(
                position_authority=params.position_authority,
                receiver=params.receiver,
                position=params.position,
                position_mint=params.position_mint,
                position_token_account=params.position_token_account,
                # token_program=TOKEN_PROGRAM_ID,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def initialize_tick_array(program_id: Pubkey, params: InitializeTickArrayParams):
        ix = instructions.initialize_tick_array(
            instructions.InitializeTickArrayArgs(
                start_tick_index=params.start_tick_index,
            ),
            instructions.InitializeTickArrayAccounts(
                whirlpool=params.whirlpool,
                funder=params.funder,
                tick_array=params.tick_array,
                # system_program=SYS_PROGRAM_ID,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def initialize_config(program_id: Pubkey, params: InitializeConfigParams):
        ix = instructions.initialize_config(
            instructions.InitializeConfigArgs(
                default_protocol_fee_rate=params.default_protocol_fee_rate,
                fee_authority=params.fee_authority,
                collect_protocol_fees_authority=params.collect_protocol_fees_authority,
                reward_emissions_super_authority=params.reward_emissions_super_authority,
            ),
            instructions.InitializeConfigAccounts(
                config=params.config,
                funder=params.funder,
                # system_program=SYS_PROGRAM_ID,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def initialize_fee_tier(program_id: Pubkey, params: InitializeFeeTierParams):
        ix = instructions.initialize_fee_tier(
            instructions.InitializeFeeTierArgs(
                tick_spacing=params.tick_spacing,
                default_fee_rate=params.default_fee_rate
            ),
            instructions.InitializeFeeTierAccounts(
                config=params.config,
                fee_tier=params.fee_tier,
                funder=params.funder,
                fee_authority=params.fee_authority,
                # system_program=SYS_PROGRAM_ID,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def initialize_pool(program_id: Pubkey, params: InitializePoolParams):
        ix = instructions.initialize_pool(
            instructions.InitializePoolArgs(
                tick_spacing=params.tick_spacing,
                initial_sqrt_price=params.initial_sqrt_price,
                bumps=types.whirlpool_bumps.WhirlpoolBumps(params.whirlpool_pda.bump),
            ),
            instructions.InitializePoolAccounts(
                whirlpools_config=params.whirlpools_config,
                token_mint_a=params.token_mint_a,
                token_mint_b=params.token_mint_b,
                funder=params.funder,
                whirlpool=params.whirlpool_pda.pubkey,
                token_vault_a=params.token_vault_a,
                token_vault_b=params.token_vault_b,
                fee_tier=params.fee_tier,
                # token_program=TOKEN_PROGRAM_ID,
                # system_program=SYS_PROGRAM_ID,
                # rent=RENT,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def initialize_reward(program_id: Pubkey, params: InitializeRewardParams):
        ix = instructions.initialize_reward(
            instructions.InitializeRewardArgs(
                reward_index=params.reward_index,
            ),
            instructions.InitializeRewardAccounts(
                reward_authority=params.reward_authority,
                funder=params.funder,
                whirlpool=params.whirlpool,
                reward_mint=params.reward_mint,
                reward_vault=params.reward_vault,
                # token_program=TOKEN_PROGRAM_ID,
                # system_program=SYS_PROGRAM_ID,
                # rent=RENT,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def collect_protocol_fees(program_id: Pubkey, params: CollectProtocolFeesParams):
        ix = instructions.collect_protocol_fees(
            instructions.CollectProtocolFeesAccounts(
                whirlpools_config=params.whirlpools_config,
                whirlpool=params.whirlpool,
                collect_protocol_fees_authority=params.collect_protocol_fees_authority,
                token_vault_a=params.token_vault_a,
                token_vault_b=params.token_vault_b,
                token_destination_a=params.token_destination_a,
                token_destination_b=params.token_destination_b,
                # token_program=TOKEN_PROGRAM_ID,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def set_collect_protocol_fees_authority(program_id: Pubkey, params: SetCollectProtocolFeesAuthorityParams):
        ix = instructions.set_collect_protocol_fees_authority(
            instructions.SetCollectProtocolFeesAuthorityAccounts(
                whirlpools_config=params.whirlpools_config,
                collect_protocol_fees_authority=params.collect_protocol_fees_authority,
                new_collect_protocol_fees_authority=params.new_collect_protocol_fees_authority,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def set_default_fee_rate(program_id: Pubkey, params: SetDefaultFeeRateParams):
        ix = instructions.set_default_fee_rate(
            instructions.SetDefaultFeeRateArgs(
                default_fee_rate=params.default_fee_rate,
            ),
            instructions.SetDefaultFeeRateAccounts(
                whirlpools_config=params.whirlpools_config,
                fee_tier=params.fee_tier,
                fee_authority=params.fee_authority,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def set_default_protocol_fee_rate(program_id: Pubkey, params: SetDefaultProtocolFeeRateParams):
        ix = instructions.set_default_protocol_fee_rate(
            instructions.SetDefaultProtocolFeeRateArgs(
                default_protocol_fee_rate=params.default_protocol_fee_rate,
            ),
            instructions.SetDefaultProtocolFeeRateAccounts(
                whirlpools_config=params.whirlpools_config,
                fee_authority=params.fee_authority,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def set_fee_authority(program_id: Pubkey, params: SetFeeAuthorityParams):
        ix = instructions.set_fee_authority(
            instructions.SetFeeAuthorityAccounts(
                whirlpools_config=params.whirlpools_config,
                fee_authority=params.fee_authority,
                new_fee_authority=params.new_fee_authority,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def set_fee_rate(program_id: Pubkey, params: SetFeeRateParams):
        ix = instructions.set_fee_rate(
            instructions.SetFeeRateArgs(
                fee_rate=params.fee_rate,
            ),
            instructions.SetFeeRateAccounts(
                whirlpools_config=params.whirlpools_config,
                whirlpool=params.whirlpool,
                fee_authority=params.fee_authority,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def set_protocol_fee_rate(program_id: Pubkey, params: SetProtocolFeeRateParams):
        ix = instructions.set_protocol_fee_rate(
            instructions.SetProtocolFeeRateArgs(
                protocol_fee_rate=params.protocol_fee_rate,
            ),
            instructions.SetProtocolFeeRateAccounts(
                whirlpools_config=params.whirlpools_config,
                whirlpool=params.whirlpool,
                fee_authority=params.fee_authority,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def set_reward_authority(program_id: Pubkey, params: SetRewardAuthorityParams):
        ix = instructions.set_reward_authority(
            instructions.SetRewardAuthorityArgs(
                reward_index=params.reward_index
            ),
            instructions.SetRewardAuthorityAccounts(
                whirlpool=params.whirlpool,
                reward_authority=params.reward_authority,
                new_reward_authority=params.new_reward_authority,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def set_reward_authority_by_super_authority(program_id: Pubkey, params: SetRewardAuthorityBySuperAuthorityParams):
        ix = instructions.set_reward_authority_by_super_authority(
            instructions.SetRewardAuthorityBySuperAuthorityArgs(
                reward_index=params.reward_index
            ),
            instructions.SetRewardAuthorityBySuperAuthorityAccounts(
                whirlpools_config=params.whirlpools_config,
                whirlpool=params.whirlpool,
                reward_emissions_super_authority=params.reward_emissions_super_authority,
                new_reward_authority=params.new_reward_authority,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def set_reward_emissions(program_id: Pubkey, params: SetRewardEmissionsParams):
        ix = instructions.set_reward_emissions(
            instructions.SetRewardEmissionsArgs(
                reward_index=params.reward_index,
                emissions_per_second_x64=params.emissions_per_second_x64,
            ),
            instructions.SetRewardEmissionsAccounts(
                whirlpool=params.whirlpool,
                reward_authority=params.reward_authority,
                reward_vault=params.reward_vault,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def set_reward_emissions_super_authority(program_id: Pubkey, params: SetRewardEmissionsSuperAuthorityParams):
        ix = instructions.set_reward_emissions_super_authority(
            instructions.SetRewardEmissionsSuperAuthorityAccounts(
                whirlpools_config=params.whirlpools_config,
                reward_emissions_super_authority=params.reward_emissions_super_authority,
                new_reward_emissions_super_authority=params.new_reward_emissions_super_authority,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def initialize_position_bundle(program_id: Pubkey, params: InitializePositionBundleParams):
        ix = instructions.initialize_position_bundle(
            instructions.InitializePositionBundleAccounts(
                position_bundle_owner=params.owner,
                position_bundle=params.position_bundle_pda.pubkey,
                position_bundle_mint=params.position_bundle_mint,
                position_bundle_token_account=params.position_bundle_token_account,
                funder=params.funder,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def initialize_position_bundle_with_metadata(program_id: Pubkey, params: InitializePositionBundleWithMetadataParams):
        ix = instructions.initialize_position_bundle_with_metadata(
            instructions.InitializePositionBundleWithMetadataAccounts(
                position_bundle_owner=params.owner,
                position_bundle=params.position_bundle_pda.pubkey,
                position_bundle_mint=params.position_bundle_mint,
                position_bundle_token_account=params.position_bundle_token_account,
                funder=params.funder,
                position_bundle_metadata=params.position_bundle_metadata_pda.pubkey,
                metadata_program=METAPLEX_METADATA_PROGRAM_ID,
                metadata_update_auth=ORCA_WHIRLPOOL_NFT_UPDATE_AUTHORITY,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def delete_position_bundle(program_id: Pubkey, params: DeletePositionBundleParams):
        ix = instructions.delete_position_bundle(
            instructions.DeletePositionBundleAccounts(
                position_bundle_owner=params.owner,
                position_bundle=params.position_bundle,
                position_bundle_mint=params.position_bundle_mint,
                position_bundle_token_account=params.position_bundle_token_account,
                receiver=params.receiver,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def open_bundled_position(program_id: Pubkey, params: OpenBundledPositionParams):
        ix = instructions.open_bundled_position(
            instructions.OpenBundledPositionArgs(
                bundle_index=params.bundle_index,
                tick_lower_index=params.tick_lower_index,
                tick_upper_index=params.tick_upper_index,
            ),
            instructions.OpenBundledPositionAccounts(
                whirlpool=params.whirlpool,
                bundled_position=params.bundled_position_pda.pubkey,
                position_bundle=params.position_bundle,
                position_bundle_token_account=params.position_bundle_token_account,
                position_bundle_authority=params.position_bundle_authority,
                funder=params.funder,
            ),
            program_id
        )
        return to_instruction([ix])

    @staticmethod
    def close_bundled_position(program_id: Pubkey, params: CloseBundledPositionParams):
        ix = instructions.close_bundled_position(
            instructions.CloseBundledPositionArgs(
                bundle_index=params.bundle_index,
            ),
            instructions.CloseBundledPositionAccounts(
                bundled_position=params.bundled_position,
                position_bundle=params.position_bundle,
                position_bundle_token_account=params.position_bundle_token_account,
                position_bundle_authority=params.position_bundle_authority,
                receiver=params.receiver,
            ),
            program_id
        )
        return to_instruction([ix])
