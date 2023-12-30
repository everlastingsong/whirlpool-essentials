from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class CloseBundledPositionArgs(typing.TypedDict):
    bundle_index: int


layout = borsh.CStruct("bundle_index" / borsh.U16)


class CloseBundledPositionAccounts(typing.TypedDict):
    bundled_position: Pubkey
    position_bundle: Pubkey
    position_bundle_token_account: Pubkey
    position_bundle_authority: Pubkey
    receiver: Pubkey


def close_bundled_position(
    args: CloseBundledPositionArgs,
    accounts: CloseBundledPositionAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["bundled_position"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["position_bundle"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["position_bundle_token_account"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["position_bundle_authority"],
            is_signer=True,
            is_writable=False,
        ),
        AccountMeta(pubkey=accounts["receiver"], is_signer=False, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b")$\xd8\xf5\x1bUgC"
    encoded_args = layout.build(
        {
            "bundle_index": args["bundle_index"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
