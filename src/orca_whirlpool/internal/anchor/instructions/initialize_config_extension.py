from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class InitializeConfigExtensionAccounts(typing.TypedDict):
    config: Pubkey
    config_extension: Pubkey
    funder: Pubkey
    fee_authority: Pubkey


def initialize_config_extension(
    accounts: InitializeConfigExtensionAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["config"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["config_extension"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["funder"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["fee_authority"], is_signer=True, is_writable=False
        ),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"7\t5\tr9\xd14"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
