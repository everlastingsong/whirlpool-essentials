from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class DecreaseLiquidityV2Args(typing.TypedDict):
    liquidity_amount: int
    token_min_a: int
    token_min_b: int
    remaining_accounts_info: typing.Optional[
        types.remaining_accounts_info.RemainingAccountsInfo
    ]


layout = borsh.CStruct(
    "liquidity_amount" / borsh.U128,
    "token_min_a" / borsh.U64,
    "token_min_b" / borsh.U64,
    "remaining_accounts_info"
    / borsh.Option(types.remaining_accounts_info.RemainingAccountsInfo.layout),
)


class DecreaseLiquidityV2Accounts(typing.TypedDict):
    whirlpool: Pubkey
    token_program_a: Pubkey
    token_program_b: Pubkey
    memo_program: Pubkey
    position_authority: Pubkey
    position: Pubkey
    position_token_account: Pubkey
    token_mint_a: Pubkey
    token_mint_b: Pubkey
    token_owner_account_a: Pubkey
    token_owner_account_b: Pubkey
    token_vault_a: Pubkey
    token_vault_b: Pubkey
    tick_array_lower: Pubkey
    tick_array_upper: Pubkey


def decrease_liquidity_v2(
    args: DecreaseLiquidityV2Args,
    accounts: DecreaseLiquidityV2Accounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["whirlpool"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["token_program_a"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_program_b"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["memo_program"], is_signer=False, is_writable=False
        ),
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
            pubkey=accounts["token_owner_account_b"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_vault_a"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_vault_b"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["tick_array_lower"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["tick_array_upper"], is_signer=False, is_writable=True
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b":\x7f\xbc>OR\xc4`"
    encoded_args = layout.build(
        {
            "liquidity_amount": args["liquidity_amount"],
            "token_min_a": args["token_min_a"],
            "token_min_b": args["token_min_b"],
            "remaining_accounts_info": (
                None
                if args["remaining_accounts_info"] is None
                else args["remaining_accounts_info"].to_encodable()
            ),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
