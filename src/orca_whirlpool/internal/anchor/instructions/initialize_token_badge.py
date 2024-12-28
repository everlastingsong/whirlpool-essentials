from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class InitializeTokenBadgeAccounts(typing.TypedDict):
    whirlpools_config: Pubkey
    whirlpools_config_extension: Pubkey
    token_badge_authority: Pubkey
    token_mint: Pubkey
    token_badge: Pubkey
    funder: Pubkey


def initialize_token_badge(
    accounts: InitializeTokenBadgeAccounts,
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
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["token_badge_authority"], is_signer=True, is_writable=False
        ),
        AccountMeta(pubkey=accounts["token_mint"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["token_badge"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["funder"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xfdM\xcd_\x1b\xe0Y\xdf"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
