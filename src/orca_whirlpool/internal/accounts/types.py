import dataclasses
from typing import Optional
from solders.pubkey import Pubkey
from ..anchor.types import WhirlpoolRewardInfo, Tick, PositionRewardInfo


@dataclasses.dataclass(frozen=True)
class WhirlpoolsConfig:
    # keyed
    pubkey: Pubkey
    # WhirlpoolsConfig
    fee_authority: Pubkey
    collect_protocol_fees_authority: Pubkey
    reward_emissions_super_authority: Pubkey
    default_protocol_fee_rate: int


@dataclasses.dataclass(frozen=True)
class FeeTier:
    # keyed
    pubkey: Pubkey
    # FeeTier
    whirlpools_config: Pubkey
    tick_spacing: int
    default_fee_rate: int


@dataclasses.dataclass(frozen=True)
class Whirlpool:
    # keyed
    pubkey: Pubkey
    # Whirlpool
    whirlpools_config: Pubkey
    whirlpool_bump: list[int]
    tick_spacing: int
    tick_spacing_seed: list[int]
    fee_rate: int
    protocol_fee_rate: int
    liquidity: int
    sqrt_price: int
    tick_current_index: int
    protocol_fee_owed_a: int
    protocol_fee_owed_b: int
    token_mint_a: Pubkey
    token_vault_a: Pubkey
    fee_growth_global_a: int
    token_mint_b: Pubkey
    token_vault_b: Pubkey
    fee_growth_global_b: int
    reward_last_updated_timestamp: int
    reward_infos: list[WhirlpoolRewardInfo]


@dataclasses.dataclass(frozen=True)
class TickArray:
    # keyed
    pubkey: Pubkey
    # TickArray
    start_tick_index: int
    ticks: list[Tick]
    whirlpool: Pubkey


@dataclasses.dataclass(frozen=True)
class Position:
    # keyed
    pubkey: Pubkey
    # Position
    whirlpool: Pubkey
    position_mint: Pubkey
    liquidity: int
    tick_lower_index: int
    tick_upper_index: int
    fee_growth_checkpoint_a: int
    fee_owed_a: int
    fee_growth_checkpoint_b: int
    fee_owed_b: int
    reward_infos: list[PositionRewardInfo]


@dataclasses.dataclass(frozen=True)
class PositionBundle:
    # keyed
    pubkey: Pubkey
    # PositionBundle
    position_bundle_mint: Pubkey
    position_bitmap: list[int]


@dataclasses.dataclass(frozen=True)
class WhirlpoolsConfigExtension:
    # keyed
    pubkey: Pubkey
    # WhirlpoolsConfigExtension
    whirlpools_config: Pubkey
    config_extension_authority: Pubkey
    token_badge_authority: Pubkey


@dataclasses.dataclass(frozen=True)
class TokenBadge:
    # keyed
    pubkey: Pubkey
    # TokenBadge
    whirlpools_config: Pubkey
    token_mint: Pubkey


@dataclasses.dataclass(frozen=True)
class AccountInfo:
    # keyed
    pubkey: Pubkey
    # token program id
    token_program_id: Pubkey
    # AccountInfo
    mint: Pubkey
    owner: Pubkey
    amount: int
    delegate: Optional[Pubkey]
    delegated_amount: int
    is_initialized: bool
    is_frozen: bool
    is_native: bool
    close_authority: Optional[Pubkey]
    tlv_data: bytes


@dataclasses.dataclass(frozen=True)
class MintInfo:
    # keyed
    pubkey: Pubkey
    # token program id
    token_program_id: Pubkey
    # MintInfo
    mint_authority: Optional[Pubkey]
    supply: int
    decimals: int
    is_initialized: bool
    freeze_authority: Optional[Pubkey]
    tlv_data: bytes
