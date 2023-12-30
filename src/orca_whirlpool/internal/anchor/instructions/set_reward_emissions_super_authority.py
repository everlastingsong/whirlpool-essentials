from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class SetRewardEmissionsSuperAuthorityAccounts(typing.TypedDict):
    whirlpools_config: Pubkey
    reward_emissions_super_authority: Pubkey
    new_reward_emissions_super_authority: Pubkey


def set_reward_emissions_super_authority(
    accounts: SetRewardEmissionsSuperAuthorityAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["whirlpools_config"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["reward_emissions_super_authority"],
            is_signer=True,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["new_reward_emissions_super_authority"],
            is_signer=False,
            is_writable=False,
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xcf\x05\xc8\xd1z8R\xb7"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
