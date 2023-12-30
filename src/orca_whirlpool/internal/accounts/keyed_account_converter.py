from typing import Optional
from solders.pubkey import Pubkey
from spl.token.core import AccountInfo as SolanapyAccountInfo, MintInfo as SolanapyMintInfo
from ..anchor.accounts import WhirlpoolsConfig as AnchorWhirlpoolsConfig, FeeTier as AnchorFeeTier
from ..anchor.accounts import Whirlpool as AnchorWhirlpool, TickArray as AnchorTickArray, Position as AnchorPosition
from ..anchor.accounts import PositionBundle as AnchorPositionBundle
from .types import WhirlpoolsConfig, FeeTier, Whirlpool, TickArray, Position, PositionBundle, AccountInfo, MintInfo


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
    def to_keyed_token_mint(pubkey: Pubkey, account: Optional[SolanapyMintInfo]) -> Optional[MintInfo]:
        if account is None:
            return None
        return MintInfo(
            pubkey=pubkey,
            mint_authority=account.mint_authority,
            supply=account.supply,
            decimals=account.decimals,
            is_initialized=account.is_initialized,
            freeze_authority=account.freeze_authority,
        )

    @staticmethod
    def to_keyed_token_account(pubkey: Pubkey, account: Optional[SolanapyAccountInfo]) -> Optional[AccountInfo]:
        if account is None:
            return None
        return AccountInfo(
            pubkey=pubkey,
            mint=account.mint,
            owner=account.owner,
            amount=account.amount,
            delegate=account.delegate,
            delegated_amount=account.delegated_amount,
            is_initialized=account.is_initialized,
            is_frozen=account.is_frozen,
            is_native=account.is_native,
            rent_exempt_reserve=account.rent_exempt_reserve,
            close_authority=account.close_authority,
        )
