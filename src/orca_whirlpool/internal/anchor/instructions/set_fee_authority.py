from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class SetFeeAuthorityAccounts(typing.TypedDict):
    whirlpools_config: Pubkey
    fee_authority: Pubkey
    new_fee_authority: Pubkey


def set_fee_authority(
    accounts: SetFeeAuthorityAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["whirlpools_config"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["fee_authority"], is_signer=True, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["new_fee_authority"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x1f\x012W\xedea\x84"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
