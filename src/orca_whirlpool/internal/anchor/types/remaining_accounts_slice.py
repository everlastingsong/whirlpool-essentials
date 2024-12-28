from __future__ import annotations
from . import (
    accounts_type,
)
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class RemainingAccountsSliceJSON(typing.TypedDict):
    accounts_type: accounts_type.AccountsTypeJSON
    length: int


@dataclass
class RemainingAccountsSlice:
    layout: typing.ClassVar = borsh.CStruct(
        "accounts_type" / accounts_type.layout, "length" / borsh.U8
    )
    accounts_type: accounts_type.AccountsTypeKind
    length: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "RemainingAccountsSlice":
        return cls(
            accounts_type=accounts_type.from_decoded(obj.accounts_type),
            length=obj.length,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "accounts_type": self.accounts_type.to_encodable(),
            "length": self.length,
        }

    def to_json(self) -> RemainingAccountsSliceJSON:
        return {"accounts_type": self.accounts_type.to_json(), "length": self.length}

    @classmethod
    def from_json(cls, obj: RemainingAccountsSliceJSON) -> "RemainingAccountsSlice":
        return cls(
            accounts_type=accounts_type.from_json(obj["accounts_type"]),
            length=obj["length"],
        )
