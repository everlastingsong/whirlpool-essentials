from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class DeleteTokenBadgeAccounts(typing.TypedDict):
    whirlpools_config: Pubkey
    whirlpools_config_extension: Pubkey
    token_badge_authority: Pubkey
    token_mint: Pubkey
    token_badge: Pubkey
    receiver: Pubkey


def delete_token_badge(
    accounts: DeleteTokenBadgeAccounts,
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
        AccountMeta(pubkey=accounts["receiver"], is_signer=False, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"5\x92D\x08\x12u\x11\xb9"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
