import dataclasses
from typing import Optional
from solana.publickey import PublicKey
from ..anchor.types import WhirlpoolRewardInfo, Tick, PositionRewardInfo


@dataclasses.dataclass(frozen=True)
class WhirlpoolsConfig:
    # keyed
    pubkey: PublicKey
    # WhirlpoolsConfig
    fee_authority: PublicKey
    collect_protocol_fees_authority: PublicKey
    reward_emissions_super_authority: PublicKey
    default_protocol_fee_rate: int


@dataclasses.dataclass(frozen=True)
class FeeTier:
    # keyed
    pubkey: PublicKey
    # FeeTier
    whirlpools_config: PublicKey
    tick_spacing: int
    default_fee_rate: int


@dataclasses.dataclass(frozen=True)
class Whirlpool:
    # keyed
    pubkey: PublicKey
    # Whirlpool
    whirlpools_config: PublicKey
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
    token_mint_a: PublicKey
    token_vault_a: PublicKey
    fee_growth_global_a: int
    token_mint_b: PublicKey
    token_vault_b: PublicKey
    fee_growth_global_b: int
    reward_last_updated_timestamp: int
    reward_infos: list[WhirlpoolRewardInfo]


@dataclasses.dataclass(frozen=True)
class TickArray:
    # keyed
    pubkey: PublicKey
    # TickArray
    start_tick_index: int
    ticks: list[Tick]
    whirlpool: PublicKey


@dataclasses.dataclass(frozen=True)
class Position:
    # keyed
    pubkey: PublicKey
    # Position
    whirlpool: PublicKey
    position_mint: PublicKey
    liquidity: int
    tick_lower_index: int
    tick_upper_index: int
    fee_growth_checkpoint_a: int
    fee_owed_a: int
    fee_growth_checkpoint_b: int
    fee_owed_b: int
    reward_infos: list[PositionRewardInfo]


@dataclasses.dataclass(frozen=True)
class AccountInfo:
    # keyed
    pubkey: PublicKey
    # AccountInfo
    mint: PublicKey
    owner: PublicKey
    amount: int
    delegate: Optional[PublicKey]
    delegated_amount: int
    is_initialized: bool
    is_frozen: bool
    is_native: bool
    rent_exempt_reserve: Optional[int]
    close_authority: Optional[PublicKey]


@dataclasses.dataclass(frozen=True)
class MintInfo:
    # keyed
    pubkey: PublicKey
    # MintInfo
    mint_authority: Optional[PublicKey]
    supply: int
    decimals: int
    is_initialized: bool
    freeze_authority: Optional[PublicKey]
