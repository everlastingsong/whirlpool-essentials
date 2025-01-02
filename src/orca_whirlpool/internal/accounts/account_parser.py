from typing import Optional
from solders.pubkey import Pubkey
from spl.token.core import AccountInfo as SolanapyAccountInfo, MintInfo as SolanapyMintInfo
from ..anchor.accounts import WhirlpoolsConfig as AnchorWhirlpoolsConfig, FeeTier as AnchorFeeTier
from ..anchor.accounts import Whirlpool as AnchorWhirlpool, TickArray as AnchorTickArray, Position as AnchorPosition
from ..anchor.accounts import PositionBundle as AnchorPositionBundle
from ..anchor.accounts import WhirlpoolsConfigExtension as AnchorWhirlpoolsConfigExtension, TokenBadge as AnchorTokenBadge
from ..utils.token_util import TokenUtil


def safe_decode(decode, data, program_id: Optional[Pubkey] = None):
    try:
        if program_id is None:
            return decode(data)
        else:
            return decode(data, program_id)
    # TODO: too broad exception catch
    except Exception:
        return None


class AccountParser:
    @staticmethod
    def parse_fee_tier(data: bytes) -> Optional[AnchorFeeTier]:
        return safe_decode(AnchorFeeTier.decode, data)

    @staticmethod
    def parse_position(data: bytes) -> Optional[AnchorPosition]:
        return safe_decode(AnchorPosition.decode, data)

    @staticmethod
    def parse_tick_array(data: bytes) -> Optional[AnchorTickArray]:
        return safe_decode(AnchorTickArray.decode, data)

    @staticmethod
    def parse_whirlpool(data: bytes) -> Optional[AnchorWhirlpool]:
        return safe_decode(AnchorWhirlpool.decode, data)

    @staticmethod
    def parse_whirlpools_config(data: bytes) -> Optional[AnchorWhirlpoolsConfig]:
        return safe_decode(AnchorWhirlpoolsConfig.decode, data)

    @staticmethod
    def parse_position_bundle(data: bytes) -> Optional[AnchorPositionBundle]:
        return safe_decode(AnchorPositionBundle.decode, data)

    @staticmethod
    def parse_whirlpools_config_extension(data: bytes) -> Optional[AnchorWhirlpoolsConfigExtension]:
        return safe_decode(AnchorWhirlpoolsConfigExtension.decode, data)

    @staticmethod
    def parse_token_badge(data: bytes) -> Optional[AnchorTokenBadge]:
        return safe_decode(AnchorTokenBadge.decode, data)

    @staticmethod
    def parse_token_mint(data: bytes, program_id: Pubkey) -> Optional[SolanapyMintInfo]:
        return safe_decode(TokenUtil.deserialize_mint, data, program_id)

    @staticmethod
    def parse_token_account(data: bytes, program_id: Pubkey) -> Optional[SolanapyAccountInfo]:
        return safe_decode(TokenUtil.deserialize_account, data, program_id)
