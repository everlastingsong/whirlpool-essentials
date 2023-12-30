from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class SetProtocolFeeRateArgs(typing.TypedDict):
    protocol_fee_rate: int


layout = borsh.CStruct("protocol_fee_rate" / borsh.U16)


class SetProtocolFeeRateAccounts(typing.TypedDict):
    whirlpools_config: Pubkey
    whirlpool: Pubkey
    fee_authority: Pubkey


def set_protocol_fee_rate(
    args: SetProtocolFeeRateArgs,
    accounts: SetProtocolFeeRateAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["whirlpools_config"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["whirlpool"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["fee_authority"], is_signer=True, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"_\x07\x042\x9aO\x9c\x83"
    encoded_args = layout.build(
        {
            "protocol_fee_rate": args["protocol_fee_rate"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
