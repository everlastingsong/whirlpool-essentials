from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class CollectProtocolFeesAccounts(typing.TypedDict):
    whirlpools_config: Pubkey
    whirlpool: Pubkey
    collect_protocol_fees_authority: Pubkey
    token_vault_a: Pubkey
    token_vault_b: Pubkey
    token_destination_a: Pubkey
    token_destination_b: Pubkey


def collect_protocol_fees(
    accounts: CollectProtocolFeesAccounts,
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
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x16C\x17b\x96\xb2F\xdc"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
