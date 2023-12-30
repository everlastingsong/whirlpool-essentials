from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class UpdateFeesAndRewardsAccounts(typing.TypedDict):
    whirlpool: Pubkey
    position: Pubkey
    tick_array_lower: Pubkey
    tick_array_upper: Pubkey


def update_fees_and_rewards(
    accounts: UpdateFeesAndRewardsAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["whirlpool"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["position"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["tick_array_lower"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["tick_array_upper"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x9a\xe6\xfa\r\xec\xd1K\xdf"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
