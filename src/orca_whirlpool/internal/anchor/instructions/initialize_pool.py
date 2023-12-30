from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class InitializePoolArgs(typing.TypedDict):
    bumps: types.whirlpool_bumps.WhirlpoolBumps
    tick_spacing: int
    initial_sqrt_price: int


layout = borsh.CStruct(
    "bumps" / types.whirlpool_bumps.WhirlpoolBumps.layout,
    "tick_spacing" / borsh.U16,
    "initial_sqrt_price" / borsh.U128,
)


class InitializePoolAccounts(typing.TypedDict):
    whirlpools_config: Pubkey
    token_mint_a: Pubkey
    token_mint_b: Pubkey
    funder: Pubkey
    whirlpool: Pubkey
    token_vault_a: Pubkey
    token_vault_b: Pubkey
    fee_tier: Pubkey


def initialize_pool(
    args: InitializePoolArgs,
    accounts: InitializePoolAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["whirlpools_config"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_mint_a"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_mint_b"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["funder"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["whirlpool"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["token_vault_a"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["token_vault_b"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["fee_tier"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"_\xb4\n\xacT\xae\xe8("
    encoded_args = layout.build(
        {
            "bumps": args["bumps"].to_encodable(),
            "tick_spacing": args["tick_spacing"],
            "initial_sqrt_price": args["initial_sqrt_price"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
