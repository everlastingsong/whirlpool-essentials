from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class CollectFeesV2Args(typing.TypedDict):
    remaining_accounts_info: typing.Optional[
        types.remaining_accounts_info.RemainingAccountsInfo
    ]


layout = borsh.CStruct(
    "remaining_accounts_info"
    / borsh.Option(types.remaining_accounts_info.RemainingAccountsInfo.layout)
)


class CollectFeesV2Accounts(typing.TypedDict):
    whirlpool: Pubkey
    position_authority: Pubkey
    position: Pubkey
    position_token_account: Pubkey
    token_mint_a: Pubkey
    token_mint_b: Pubkey
    token_owner_account_a: Pubkey
    token_vault_a: Pubkey
    token_owner_account_b: Pubkey
    token_vault_b: Pubkey
    token_program_a: Pubkey
    token_program_b: Pubkey
    memo_program: Pubkey


def collect_fees_v2(
    args: CollectFeesV2Args,
    accounts: CollectFeesV2Accounts,
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
            pubkey=accounts["token_mint_a"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_mint_b"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_owner_account_a"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_vault_a"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_owner_account_b"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_vault_b"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_program_a"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_program_b"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["memo_program"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xcfu_\xbf\xe5\xb4\xe2\x0f"
    encoded_args = layout.build(
        {
            "remaining_accounts_info": (
                None
                if args["remaining_accounts_info"] is None
                else args["remaining_accounts_info"].to_encodable()
            ),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
