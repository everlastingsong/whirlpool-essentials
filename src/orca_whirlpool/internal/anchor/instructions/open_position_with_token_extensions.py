from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class OpenPositionWithTokenExtensionsArgs(typing.TypedDict):
    tick_lower_index: int
    tick_upper_index: int
    with_token_metadata_extension: bool


layout = borsh.CStruct(
    "tick_lower_index" / borsh.I32,
    "tick_upper_index" / borsh.I32,
    "with_token_metadata_extension" / borsh.Bool,
)


class OpenPositionWithTokenExtensionsAccounts(typing.TypedDict):
    funder: Pubkey
    owner: Pubkey
    position: Pubkey
    position_mint: Pubkey
    position_token_account: Pubkey
    whirlpool: Pubkey
    token2022_program: Pubkey
    metadata_update_auth: Pubkey


def open_position_with_token_extensions(
    args: OpenPositionWithTokenExtensionsArgs,
    accounts: OpenPositionWithTokenExtensionsAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["funder"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["position"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["position_mint"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["position_token_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["whirlpool"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["token2022_program"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=ASSOCIATED_TOKEN_PROGRAM_ID, is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["metadata_update_auth"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xd4/_\\rf\x83\xfa"
    encoded_args = layout.build(
        {
            "tick_lower_index": args["tick_lower_index"],
            "tick_upper_index": args["tick_upper_index"],
            "with_token_metadata_extension": args["with_token_metadata_extension"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
