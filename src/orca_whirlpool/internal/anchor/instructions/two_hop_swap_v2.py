from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class TwoHopSwapV2Args(typing.TypedDict):
    amount: int
    other_amount_threshold: int
    amount_specified_is_input: bool
    a_to_b_one: bool
    a_to_b_two: bool
    sqrt_price_limit_one: int
    sqrt_price_limit_two: int
    remaining_accounts_info: typing.Optional[
        types.remaining_accounts_info.RemainingAccountsInfo
    ]


layout = borsh.CStruct(
    "amount" / borsh.U64,
    "other_amount_threshold" / borsh.U64,
    "amount_specified_is_input" / borsh.Bool,
    "a_to_b_one" / borsh.Bool,
    "a_to_b_two" / borsh.Bool,
    "sqrt_price_limit_one" / borsh.U128,
    "sqrt_price_limit_two" / borsh.U128,
    "remaining_accounts_info"
    / borsh.Option(types.remaining_accounts_info.RemainingAccountsInfo.layout),
)


class TwoHopSwapV2Accounts(typing.TypedDict):
    whirlpool_one: Pubkey
    whirlpool_two: Pubkey
    token_mint_input: Pubkey
    token_mint_intermediate: Pubkey
    token_mint_output: Pubkey
    token_program_input: Pubkey
    token_program_intermediate: Pubkey
    token_program_output: Pubkey
    token_owner_account_input: Pubkey
    token_vault_one_input: Pubkey
    token_vault_one_intermediate: Pubkey
    token_vault_two_intermediate: Pubkey
    token_vault_two_output: Pubkey
    token_owner_account_output: Pubkey
    token_authority: Pubkey
    tick_array_one0: Pubkey
    tick_array_one1: Pubkey
    tick_array_one2: Pubkey
    tick_array_two0: Pubkey
    tick_array_two1: Pubkey
    tick_array_two2: Pubkey
    oracle_one: Pubkey
    oracle_two: Pubkey
    memo_program: Pubkey


def two_hop_swap_v2(
    args: TwoHopSwapV2Args,
    accounts: TwoHopSwapV2Accounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["whirlpool_one"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["whirlpool_two"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_mint_input"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_mint_intermediate"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["token_mint_output"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_program_input"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_program_intermediate"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["token_program_output"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_owner_account_input"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["token_vault_one_input"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_vault_one_intermediate"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["token_vault_two_intermediate"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["token_vault_two_output"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_owner_account_output"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["token_authority"], is_signer=True, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["tick_array_one0"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["tick_array_one1"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["tick_array_one2"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["tick_array_two0"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["tick_array_two1"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["tick_array_two2"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["oracle_one"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["oracle_two"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["memo_program"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xba\x8f\xd1\x1d\xfe\x02\xc2u"
    encoded_args = layout.build(
        {
            "amount": args["amount"],
            "other_amount_threshold": args["other_amount_threshold"],
            "amount_specified_is_input": args["amount_specified_is_input"],
            "a_to_b_one": args["a_to_b_one"],
            "a_to_b_two": args["a_to_b_two"],
            "sqrt_price_limit_one": args["sqrt_price_limit_one"],
            "sqrt_price_limit_two": args["sqrt_price_limit_two"],
            "remaining_accounts_info": (
                None
                if args["remaining_accounts_info"] is None
                else args["remaining_accounts_info"].to_encodable()
            ),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
