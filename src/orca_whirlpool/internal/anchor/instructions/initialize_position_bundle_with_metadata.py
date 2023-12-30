from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class InitializePositionBundleWithMetadataAccounts(typing.TypedDict):
    position_bundle: Pubkey
    position_bundle_mint: Pubkey
    position_bundle_metadata: Pubkey
    position_bundle_token_account: Pubkey
    position_bundle_owner: Pubkey
    funder: Pubkey
    metadata_update_auth: Pubkey
    metadata_program: Pubkey


def initialize_position_bundle_with_metadata(
    accounts: InitializePositionBundleWithMetadataAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["position_bundle"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["position_bundle_mint"], is_signer=True, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["position_bundle_metadata"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["position_bundle_token_account"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["position_bundle_owner"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["funder"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["metadata_update_auth"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=ASSOCIATED_TOKEN_PROGRAM_ID, is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["metadata_program"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"]|\x10\xb3\xf9\x83s\xf5"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
