from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class DeletePositionBundleAccounts(typing.TypedDict):
    position_bundle: Pubkey
    position_bundle_mint: Pubkey
    position_bundle_token_account: Pubkey
    position_bundle_owner: Pubkey
    receiver: Pubkey


def delete_position_bundle(
    accounts: DeletePositionBundleAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["position_bundle"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["position_bundle_mint"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["position_bundle_token_account"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["position_bundle_owner"], is_signer=True, is_writable=False
        ),
        AccountMeta(pubkey=accounts["receiver"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"d\x19c\x02\xd9\xef|\xad"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
