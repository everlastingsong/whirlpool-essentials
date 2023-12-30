from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class InitializeConfigArgs(typing.TypedDict):
    fee_authority: Pubkey
    collect_protocol_fees_authority: Pubkey
    reward_emissions_super_authority: Pubkey
    default_protocol_fee_rate: int


layout = borsh.CStruct(
    "fee_authority" / BorshPubkey,
    "collect_protocol_fees_authority" / BorshPubkey,
    "reward_emissions_super_authority" / BorshPubkey,
    "default_protocol_fee_rate" / borsh.U16,
)


class InitializeConfigAccounts(typing.TypedDict):
    config: Pubkey
    funder: Pubkey


def initialize_config(
    args: InitializeConfigArgs,
    accounts: InitializeConfigAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["config"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["funder"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xd0\x7f\x15\x01\xc2\xbe\xc4F"
    encoded_args = layout.build(
        {
            "fee_authority": args["fee_authority"],
            "collect_protocol_fees_authority": args["collect_protocol_fees_authority"],
            "reward_emissions_super_authority": args[
                "reward_emissions_super_authority"
            ],
            "default_protocol_fee_rate": args["default_protocol_fee_rate"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
