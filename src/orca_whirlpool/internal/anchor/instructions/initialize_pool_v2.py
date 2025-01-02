from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class InitializePoolV2Args(typing.TypedDict):
    tick_spacing: int
    initial_sqrt_price: int


layout = borsh.CStruct("tick_spacing" / borsh.U16, "initial_sqrt_price" / borsh.U128)


class InitializePoolV2Accounts(typing.TypedDict):
    whirlpools_config: Pubkey
    token_mint_a: Pubkey
    token_mint_b: Pubkey
    token_badge_a: Pubkey
    token_badge_b: Pubkey
    funder: Pubkey
    whirlpool: Pubkey
    token_vault_a: Pubkey
    token_vault_b: Pubkey
    fee_tier: Pubkey
    token_program_a: Pubkey
    token_program_b: Pubkey


def initialize_pool_v2(
    args: InitializePoolV2Args,
    accounts: InitializePoolV2Accounts,
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
        AccountMeta(
            pubkey=accounts["token_badge_a"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_badge_b"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["funder"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["whirlpool"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["token_vault_a"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["token_vault_b"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["fee_tier"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["token_program_a"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_program_b"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xcf-W\xf2\x1b?\xccC"
    encoded_args = layout.build(
        {
            "tick_spacing": args["tick_spacing"],
            "initial_sqrt_price": args["initial_sqrt_price"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
