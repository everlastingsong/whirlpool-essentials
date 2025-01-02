from __future__ import annotations
from . import (
    remaining_accounts_slice,
)
import typing
from dataclasses import dataclass
from construct import Container, Construct
import borsh_construct as borsh


class RemainingAccountsInfoJSON(typing.TypedDict):
    slices: list[remaining_accounts_slice.RemainingAccountsSliceJSON]


@dataclass
class RemainingAccountsInfo:
    layout: typing.ClassVar = borsh.CStruct(
        "slices"
        / borsh.Vec(
            typing.cast(
                Construct, remaining_accounts_slice.RemainingAccountsSlice.layout
            )
        )
    )
    slices: list[remaining_accounts_slice.RemainingAccountsSlice]

    @classmethod
    def from_decoded(cls, obj: Container) -> "RemainingAccountsInfo":
        return cls(
            slices=list(
                map(
                    lambda item: remaining_accounts_slice.RemainingAccountsSlice.from_decoded(
                        item
                    ),
                    obj.slices,
                )
            )
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"slices": list(map(lambda item: item.to_encodable(), self.slices))}

    def to_json(self) -> RemainingAccountsInfoJSON:
        return {"slices": list(map(lambda item: item.to_json(), self.slices))}

    @classmethod
    def from_json(cls, obj: RemainingAccountsInfoJSON) -> "RemainingAccountsInfo":
        return cls(
            slices=list(
                map(
                    lambda item: remaining_accounts_slice.RemainingAccountsSlice.from_json(
                        item
                    ),
                    obj["slices"],
                )
            )
        )
