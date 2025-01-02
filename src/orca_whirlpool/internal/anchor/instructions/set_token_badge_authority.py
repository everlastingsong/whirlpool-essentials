from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class SetTokenBadgeAuthorityAccounts(typing.TypedDict):
    whirlpools_config: Pubkey
    whirlpools_config_extension: Pubkey
    config_extension_authority: Pubkey
    new_token_badge_authority: Pubkey


def set_token_badge_authority(
    accounts: SetTokenBadgeAuthorityAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["whirlpools_config"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["whirlpools_config_extension"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["config_extension_authority"],
            is_signer=True,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["new_token_badge_authority"],
            is_signer=False,
            is_writable=False,
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xcf\xca\x04 \xcdO\r\xb2"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
