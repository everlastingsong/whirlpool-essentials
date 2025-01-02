from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class ClosePositionWithTokenExtensionsAccounts(typing.TypedDict):
    position_authority: Pubkey
    receiver: Pubkey
    position: Pubkey
    position_mint: Pubkey
    position_token_account: Pubkey
    token2022_program: Pubkey


def close_position_with_token_extensions(
    accounts: ClosePositionWithTokenExtensionsAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["position_authority"], is_signer=True, is_writable=False
        ),
        AccountMeta(pubkey=accounts["receiver"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["position"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["position_mint"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["position_token_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token2022_program"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x01\xb6\x87;\x9b\x19c\xdf"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
