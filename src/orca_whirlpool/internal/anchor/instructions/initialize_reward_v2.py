from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class InitializeRewardV2Args(typing.TypedDict):
    reward_index: int


layout = borsh.CStruct("reward_index" / borsh.U8)


class InitializeRewardV2Accounts(typing.TypedDict):
    reward_authority: Pubkey
    funder: Pubkey
    whirlpool: Pubkey
    reward_mint: Pubkey
    reward_token_badge: Pubkey
    reward_vault: Pubkey
    reward_token_program: Pubkey


def initialize_reward_v2(
    args: InitializeRewardV2Args,
    accounts: InitializeRewardV2Accounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["reward_authority"], is_signer=True, is_writable=False
        ),
        AccountMeta(pubkey=accounts["funder"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["whirlpool"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["reward_mint"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["reward_token_badge"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["reward_vault"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["reward_token_program"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"[\x01M2\xeb\xe5\x851"
    encoded_args = layout.build(
        {
            "reward_index": args["reward_index"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
