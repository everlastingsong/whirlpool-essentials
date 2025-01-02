from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class SetRewardEmissionsV2Args(typing.TypedDict):
    reward_index: int
    emissions_per_second_x64: int


layout = borsh.CStruct(
    "reward_index" / borsh.U8, "emissions_per_second_x64" / borsh.U128
)


class SetRewardEmissionsV2Accounts(typing.TypedDict):
    whirlpool: Pubkey
    reward_authority: Pubkey
    reward_vault: Pubkey


def set_reward_emissions_v2(
    args: SetRewardEmissionsV2Args,
    accounts: SetRewardEmissionsV2Accounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["whirlpool"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["reward_authority"], is_signer=True, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["reward_vault"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"r\xe4H \xc10\xa0f"
    encoded_args = layout.build(
        {
            "reward_index": args["reward_index"],
            "emissions_per_second_x64": args["emissions_per_second_x64"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
