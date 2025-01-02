from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class CollectRewardV2Args(typing.TypedDict):
    reward_index: int
    remaining_accounts_info: typing.Optional[
        types.remaining_accounts_info.RemainingAccountsInfo
    ]


layout = borsh.CStruct(
    "reward_index" / borsh.U8,
    "remaining_accounts_info"
    / borsh.Option(types.remaining_accounts_info.RemainingAccountsInfo.layout),
)


class CollectRewardV2Accounts(typing.TypedDict):
    whirlpool: Pubkey
    position_authority: Pubkey
    position: Pubkey
    position_token_account: Pubkey
    reward_owner_account: Pubkey
    reward_mint: Pubkey
    reward_vault: Pubkey
    reward_token_program: Pubkey
    memo_program: Pubkey


def collect_reward_v2(
    args: CollectRewardV2Args,
    accounts: CollectRewardV2Accounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["whirlpool"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["position_authority"], is_signer=True, is_writable=False
        ),
        AccountMeta(pubkey=accounts["position"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["position_token_account"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["reward_owner_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["reward_mint"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["reward_vault"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["reward_token_program"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["memo_program"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xb1k%\xb4\xa0\x131\xd1"
    encoded_args = layout.build(
        {
            "reward_index": args["reward_index"],
            "remaining_accounts_info": (
                None
                if args["remaining_accounts_info"] is None
                else args["remaining_accounts_info"].to_encodable()
            ),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
