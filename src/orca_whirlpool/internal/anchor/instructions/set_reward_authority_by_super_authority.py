from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class SetRewardAuthorityBySuperAuthorityArgs(typing.TypedDict):
    reward_index: int


layout = borsh.CStruct("reward_index" / borsh.U8)


class SetRewardAuthorityBySuperAuthorityAccounts(typing.TypedDict):
    whirlpools_config: Pubkey
    whirlpool: Pubkey
    reward_emissions_super_authority: Pubkey
    new_reward_authority: Pubkey


def set_reward_authority_by_super_authority(
    args: SetRewardAuthorityBySuperAuthorityArgs,
    accounts: SetRewardAuthorityBySuperAuthorityAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["whirlpools_config"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["whirlpool"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["reward_emissions_super_authority"],
            is_signer=True,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["new_reward_authority"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xf0\x9a\xc9\xc6\x94]8\x19"
    encoded_args = layout.build(
        {
            "reward_index": args["reward_index"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
