from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class TwoHopSwapArgs(typing.TypedDict):
    amount: int
    other_amount_threshold: int
    amount_specified_is_input: bool
    a_to_b_one: bool
    a_to_b_two: bool
    sqrt_price_limit_one: int
    sqrt_price_limit_two: int


layout = borsh.CStruct(
    "amount" / borsh.U64,
    "other_amount_threshold" / borsh.U64,
    "amount_specified_is_input" / borsh.Bool,
    "a_to_b_one" / borsh.Bool,
    "a_to_b_two" / borsh.Bool,
    "sqrt_price_limit_one" / borsh.U128,
    "sqrt_price_limit_two" / borsh.U128,
)


class TwoHopSwapAccounts(typing.TypedDict):
    token_authority: Pubkey
    whirlpool_one: Pubkey
    whirlpool_two: Pubkey
    token_owner_account_one_a: Pubkey
    token_vault_one_a: Pubkey
    token_owner_account_one_b: Pubkey
    token_vault_one_b: Pubkey
    token_owner_account_two_a: Pubkey
    token_vault_two_a: Pubkey
    token_owner_account_two_b: Pubkey
    token_vault_two_b: Pubkey
    tick_array_one0: Pubkey
    tick_array_one1: Pubkey
    tick_array_one2: Pubkey
    tick_array_two0: Pubkey
    tick_array_two1: Pubkey
    tick_array_two2: Pubkey
    oracle_one: Pubkey
    oracle_two: Pubkey


def two_hop_swap(
    args: TwoHopSwapArgs,
    accounts: TwoHopSwapAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["token_authority"], is_signer=True, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["whirlpool_one"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["whirlpool_two"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_owner_account_one_a"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["token_vault_one_a"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_owner_account_one_b"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["token_vault_one_b"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_owner_account_two_a"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["token_vault_two_a"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_owner_account_two_b"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["token_vault_two_b"], is_signer=False, is_writable=True
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
        AccountMeta(pubkey=accounts["oracle_one"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["oracle_two"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xc3`\xedlD\xa2\xdb\xe6"
    encoded_args = layout.build(
        {
            "amount": args["amount"],
            "other_amount_threshold": args["other_amount_threshold"],
            "amount_specified_is_input": args["amount_specified_is_input"],
            "a_to_b_one": args["a_to_b_one"],
            "a_to_b_two": args["a_to_b_two"],
            "sqrt_price_limit_one": args["sqrt_price_limit_one"],
            "sqrt_price_limit_two": args["sqrt_price_limit_two"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
