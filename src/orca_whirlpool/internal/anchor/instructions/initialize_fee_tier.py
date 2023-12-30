from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class InitializeFeeTierArgs(typing.TypedDict):
    tick_spacing: int
    default_fee_rate: int


layout = borsh.CStruct("tick_spacing" / borsh.U16, "default_fee_rate" / borsh.U16)


class InitializeFeeTierAccounts(typing.TypedDict):
    config: Pubkey
    fee_tier: Pubkey
    funder: Pubkey
    fee_authority: Pubkey


def initialize_fee_tier(
    args: InitializeFeeTierArgs,
    accounts: InitializeFeeTierAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["config"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["fee_tier"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["funder"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["fee_authority"], is_signer=True, is_writable=False
        ),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xb7J\x9c\xa0p\x02*\x1e"
    encoded_args = layout.build(
        {
            "tick_spacing": args["tick_spacing"],
            "default_fee_rate": args["default_fee_rate"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
