from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class SetDefaultFeeRateArgs(typing.TypedDict):
    default_fee_rate: int


layout = borsh.CStruct("default_fee_rate" / borsh.U16)


class SetDefaultFeeRateAccounts(typing.TypedDict):
    whirlpools_config: Pubkey
    fee_tier: Pubkey
    fee_authority: Pubkey


def set_default_fee_rate(
    args: SetDefaultFeeRateArgs,
    accounts: SetDefaultFeeRateAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["whirlpools_config"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["fee_tier"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["fee_authority"], is_signer=True, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"v\xd7\xd6\x9d\xb6\xe5\xd0\xe4"
    encoded_args = layout.build(
        {
            "default_fee_rate": args["default_fee_rate"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
