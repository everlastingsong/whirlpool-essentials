from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class OpenBundledPositionArgs(typing.TypedDict):
    bundle_index: int
    tick_lower_index: int
    tick_upper_index: int


layout = borsh.CStruct(
    "bundle_index" / borsh.U16,
    "tick_lower_index" / borsh.I32,
    "tick_upper_index" / borsh.I32,
)


class OpenBundledPositionAccounts(typing.TypedDict):
    bundled_position: Pubkey
    position_bundle: Pubkey
    position_bundle_token_account: Pubkey
    position_bundle_authority: Pubkey
    whirlpool: Pubkey
    funder: Pubkey


def open_bundled_position(
    args: OpenBundledPositionArgs,
    accounts: OpenBundledPositionAccounts,
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
        AccountMeta(pubkey=accounts["whirlpool"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["funder"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xa9q~\xab\xd5\xac\xd41"
    encoded_args = layout.build(
        {
            "bundle_index": args["bundle_index"],
            "tick_lower_index": args["tick_lower_index"],
            "tick_upper_index": args["tick_upper_index"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
