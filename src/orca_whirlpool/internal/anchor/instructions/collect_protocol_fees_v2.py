from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class CollectProtocolFeesV2Args(typing.TypedDict):
    remaining_accounts_info: typing.Optional[
        types.remaining_accounts_info.RemainingAccountsInfo
    ]


layout = borsh.CStruct(
    "remaining_accounts_info"
    / borsh.Option(types.remaining_accounts_info.RemainingAccountsInfo.layout)
)


class CollectProtocolFeesV2Accounts(typing.TypedDict):
    whirlpools_config: Pubkey
    whirlpool: Pubkey
    collect_protocol_fees_authority: Pubkey
    token_mint_a: Pubkey
    token_mint_b: Pubkey
    token_vault_a: Pubkey
    token_vault_b: Pubkey
    token_destination_a: Pubkey
    token_destination_b: Pubkey
    token_program_a: Pubkey
    token_program_b: Pubkey
    memo_program: Pubkey


def collect_protocol_fees_v2(
    args: CollectProtocolFeesV2Args,
    accounts: CollectProtocolFeesV2Accounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["whirlpools_config"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["whirlpool"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["collect_protocol_fees_authority"],
            is_signer=True,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["token_mint_a"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_mint_b"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_vault_a"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_vault_b"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_destination_a"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_destination_b"], is_signer=False, is_writable=True
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
    identifier = b"g\x80\xde\x86r\xc8\x16\xc8"
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
