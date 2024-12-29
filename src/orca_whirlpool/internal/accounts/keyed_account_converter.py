from typing import Optional
from solders.pubkey import Pubkey
from ..anchor.accounts import WhirlpoolsConfig as AnchorWhirlpoolsConfig, FeeTier as AnchorFeeTier
from ..anchor.accounts import Whirlpool as AnchorWhirlpool, TickArray as AnchorTickArray, Position as AnchorPosition
from ..anchor.accounts import PositionBundle as AnchorPositionBundle, TokenBadge as AnchorTokenBadge
from ..anchor.accounts import WhirlpoolsConfigExtension as AnchorWhirlpoolsConfigExtension
from .types import WhirlpoolsConfig, FeeTier, Whirlpool, TickArray, Position, PositionBundle, WhirlpoolsConfigExtension
from .types import TokenBadge, AccountInfo, MintInfo
from ..utils.token_util import RawMintInfo, RawAccountInfo


class KeyedAccountConverter:
    @staticmethod
    def to_keyed_fee_tier(pubkey: Pubkey, account: Optional[AnchorFeeTier]) -> Optional[FeeTier]:
        if account is None:
            return None
        return FeeTier(
            pubkey=pubkey,
            whirlpools_config=account.whirlpools_config,
            tick_spacing=account.tick_spacing,
            default_fee_rate=account.default_fee_rate,
        )

    @staticmethod
    def to_keyed_position(pubkey: Pubkey, account: Optional[AnchorPosition]) -> Optional[Position]:
        if account is None:
            return None
        return Position(
            pubkey=pubkey,
            whirlpool=account.whirlpool,
            position_mint=account.position_mint,
            liquidity=account.liquidity,
            tick_lower_index=account.tick_lower_index,
            tick_upper_index=account.tick_upper_index,
            fee_growth_checkpoint_a=account.fee_growth_checkpoint_a,
            fee_owed_a=account.fee_owed_a,
            fee_growth_checkpoint_b=account.fee_growth_checkpoint_b,
            fee_owed_b=account.fee_owed_b,
            reward_infos=account.reward_infos,
        )

    @staticmethod
    def to_keyed_tick_array(pubkey: Pubkey, account: Optional[AnchorTickArray]) -> Optional[TickArray]:
        if account is None:
            return None
        return TickArray(
            pubkey=pubkey,
            start_tick_index=account.start_tick_index,
            ticks=account.ticks,
            whirlpool=account.whirlpool,
        )

    @staticmethod
    def to_keyed_whirlpool(pubkey: Pubkey, account: Optional[AnchorWhirlpool]) -> Optional[Whirlpool]:
        if account is None:
            return None
        return Whirlpool(
            pubkey=pubkey,
            whirlpools_config=account.whirlpools_config,
            whirlpool_bump=account.whirlpool_bump,
            tick_spacing=account.tick_spacing,
            tick_spacing_seed=account.tick_spacing_seed,
            fee_rate=account.fee_rate,
            protocol_fee_rate=account.protocol_fee_rate,
            liquidity=account.liquidity,
            sqrt_price=account.sqrt_price,
            tick_current_index=account.tick_current_index,
            protocol_fee_owed_a=account.protocol_fee_owed_a,
            protocol_fee_owed_b=account.protocol_fee_owed_b,
            token_mint_a=account.token_mint_a,
            token_vault_a=account.token_vault_a,
            fee_growth_global_a=account.fee_growth_global_a,
            token_mint_b=account.token_mint_b,
            token_vault_b=account.token_vault_b,
            fee_growth_global_b=account.fee_growth_global_b,
            reward_last_updated_timestamp=account.reward_last_updated_timestamp,
            reward_infos=account.reward_infos,
        )

    @staticmethod
    def to_keyed_whirlpools_config(pubkey: Pubkey, account: Optional[AnchorWhirlpoolsConfig]) -> Optional[WhirlpoolsConfig]:
        if account is None:
            return None
        return WhirlpoolsConfig(
            pubkey=pubkey,
            fee_authority=account.fee_authority,
            collect_protocol_fees_authority=account.collect_protocol_fees_authority,
            reward_emissions_super_authority=account.reward_emissions_super_authority,
            default_protocol_fee_rate=account.default_protocol_fee_rate,
        )

    @staticmethod
    def to_keyed_position_bundle(pubkey: Pubkey, account: Optional[AnchorPositionBundle]) -> Optional[PositionBundle]:
        if account is None:
            return None
        return PositionBundle(
            pubkey=pubkey,
            position_bundle_mint=account.position_bundle_mint,
            position_bitmap=account.position_bitmap,
        )

    @staticmethod
    def to_keyed_whirlpools_config_extension(pubkey: Pubkey, account: Optional[AnchorWhirlpoolsConfigExtension]) -> Optional[WhirlpoolsConfigExtension]:
        if account is None:
            return None
        return WhirlpoolsConfigExtension(
            pubkey=pubkey,
            whirlpools_config=account.whirlpools_config,
            config_extension_authority=account.config_extension_authority,
            token_badge_authority=account.token_badge_authority,
        )

    @staticmethod
    def to_keyed_token_badge(pubkey: Pubkey, account: Optional[AnchorTokenBadge]) -> Optional[TokenBadge]:
        if account is None:
            return None
        return TokenBadge(
            pubkey=pubkey,
            whirlpools_config=account.whirlpools_config,
            token_mint=account.token_mint,
        )

    @staticmethod
    def to_keyed_token_mint(pubkey: Pubkey, account: Optional[RawMintInfo]) -> Optional[MintInfo]:
        if account is None:
            return None
        return MintInfo(
            pubkey=pubkey,
            token_program_id=account.token_program_id,
            mint_authority=account.mint_authority,
            supply=account.supply,
            decimals=account.decimals,
            is_initialized=account.is_initialized,
            freeze_authority=account.freeze_authority,
            tlv_data=account.tlv_data,
        )

    @staticmethod
    def to_keyed_token_account(pubkey: Pubkey, account: Optional[RawAccountInfo]) -> Optional[AccountInfo]:
        if account is None:
            return None
        return AccountInfo(
            pubkey=pubkey,
            token_program_id=account.token_program_id,
            mint=account.mint,
            owner=account.owner,
            amount=account.amount,
            delegate=account.delegate,
            delegated_amount=account.delegated_amount,
            is_initialized=account.is_initialized,
            is_frozen=account.is_frozen,
            is_native=account.is_native,
            close_authority=account.close_authority,
            tlv_data=account.tlv_data,
        )
