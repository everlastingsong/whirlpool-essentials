import dataclasses
from typing import List, Optional
from solders.pubkey import Pubkey
from solders.instruction import AccountMeta
from ..anchor.types.remaining_accounts_info import RemainingAccountsInfo
from ..anchor.types.remaining_accounts_slice import RemainingAccountsSlice
from ..anchor.types.accounts_type import (
    TransferHookA,
    TransferHookB,
    TransferHookReward,
    TransferHookInput,
    TransferHookIntermediate,
    TransferHookOutput,
    SupplementalTickArrays,
    SupplementalTickArraysOne,
    SupplementalTickArraysTwo,
)
from ..types.enums import RemainingAccountsType
from ..invariant import unreachable


def map_accounts_type_to_anchor_accounts_type(accounts_type: RemainingAccountsType):
    match accounts_type:
        case RemainingAccountsType.TransferHookA:
            return TransferHookA()
        case RemainingAccountsType.TransferHookB:
            return TransferHookB()
        case RemainingAccountsType.TransferHookReward:
            return TransferHookReward()
        case RemainingAccountsType.TransferHookInput:
            return TransferHookInput()
        case RemainingAccountsType.TransferHookIntermediate:
            return TransferHookIntermediate()
        case RemainingAccountsType.TransferHookOutput:
            return TransferHookOutput()
        case RemainingAccountsType.SupplementalTickArrays:
            return SupplementalTickArrays()
        case RemainingAccountsType.SupplementalTickArraysOne:
            return SupplementalTickArraysOne()
        case RemainingAccountsType.SupplementalTickArraysTwo:
            return SupplementalTickArraysTwo()

    unreachable("Unknown remaining accounts type")


@dataclasses.dataclass(frozen=True)
class RemainingAccountsInfoAndAccountMetas:
    remaining_accounts_info: Optional[RemainingAccountsInfo]
    remaining_accounts: Optional[List[AccountMeta]]


class RemainingAccountsBuilder:
    remaining_accounts: List[AccountMeta]
    slices: List[RemainingAccountsSlice]

    def __init__(self):
        self.remaining_accounts = []
        self.slices = []

    def add_slice(
        self,
        accounts_type: RemainingAccountsType,
        accounts: Optional[List[AccountMeta]]
    ):
        if accounts is not None and len(accounts) > 0:
            self.remaining_accounts.extend(accounts)
            self.slices.append(RemainingAccountsSlice(
                accounts_type=map_accounts_type_to_anchor_accounts_type(accounts_type),
                length=len(accounts)
            ))

        return self

    def build(self) -> RemainingAccountsInfoAndAccountMetas:
        if len(self.slices) == 0:
            return RemainingAccountsInfoAndAccountMetas(
                remaining_accounts_info=None,
                remaining_accounts=None,
            )
        else:
            return RemainingAccountsInfoAndAccountMetas(
                remaining_accounts_info=RemainingAccountsInfo(
                    slices=self.slices
                ),
                remaining_accounts=self.remaining_accounts,
            )

    @staticmethod
    def to_supplemental_tick_array_account_metas(
        accounts: Optional[List[Pubkey]]
    ):
        if accounts is None:
            return None

        return list(map(lambda k: AccountMeta(k, False, True), accounts))
