from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class TransferHookAJSON(typing.TypedDict):
    kind: typing.Literal["TransferHookA"]


class TransferHookBJSON(typing.TypedDict):
    kind: typing.Literal["TransferHookB"]


class TransferHookRewardJSON(typing.TypedDict):
    kind: typing.Literal["TransferHookReward"]


class TransferHookInputJSON(typing.TypedDict):
    kind: typing.Literal["TransferHookInput"]


class TransferHookIntermediateJSON(typing.TypedDict):
    kind: typing.Literal["TransferHookIntermediate"]


class TransferHookOutputJSON(typing.TypedDict):
    kind: typing.Literal["TransferHookOutput"]


class SupplementalTickArraysJSON(typing.TypedDict):
    kind: typing.Literal["SupplementalTickArrays"]


class SupplementalTickArraysOneJSON(typing.TypedDict):
    kind: typing.Literal["SupplementalTickArraysOne"]


class SupplementalTickArraysTwoJSON(typing.TypedDict):
    kind: typing.Literal["SupplementalTickArraysTwo"]


@dataclass
class TransferHookA:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "TransferHookA"

    @classmethod
    def to_json(cls) -> TransferHookAJSON:
        return TransferHookAJSON(
            kind="TransferHookA",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TransferHookA": {},
        }


@dataclass
class TransferHookB:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "TransferHookB"

    @classmethod
    def to_json(cls) -> TransferHookBJSON:
        return TransferHookBJSON(
            kind="TransferHookB",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TransferHookB": {},
        }


@dataclass
class TransferHookReward:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "TransferHookReward"

    @classmethod
    def to_json(cls) -> TransferHookRewardJSON:
        return TransferHookRewardJSON(
            kind="TransferHookReward",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TransferHookReward": {},
        }


@dataclass
class TransferHookInput:
    discriminator: typing.ClassVar = 3
    kind: typing.ClassVar = "TransferHookInput"

    @classmethod
    def to_json(cls) -> TransferHookInputJSON:
        return TransferHookInputJSON(
            kind="TransferHookInput",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TransferHookInput": {},
        }


@dataclass
class TransferHookIntermediate:
    discriminator: typing.ClassVar = 4
    kind: typing.ClassVar = "TransferHookIntermediate"

    @classmethod
    def to_json(cls) -> TransferHookIntermediateJSON:
        return TransferHookIntermediateJSON(
            kind="TransferHookIntermediate",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TransferHookIntermediate": {},
        }


@dataclass
class TransferHookOutput:
    discriminator: typing.ClassVar = 5
    kind: typing.ClassVar = "TransferHookOutput"

    @classmethod
    def to_json(cls) -> TransferHookOutputJSON:
        return TransferHookOutputJSON(
            kind="TransferHookOutput",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TransferHookOutput": {},
        }


@dataclass
class SupplementalTickArrays:
    discriminator: typing.ClassVar = 6
    kind: typing.ClassVar = "SupplementalTickArrays"

    @classmethod
    def to_json(cls) -> SupplementalTickArraysJSON:
        return SupplementalTickArraysJSON(
            kind="SupplementalTickArrays",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "SupplementalTickArrays": {},
        }


@dataclass
class SupplementalTickArraysOne:
    discriminator: typing.ClassVar = 7
    kind: typing.ClassVar = "SupplementalTickArraysOne"

    @classmethod
    def to_json(cls) -> SupplementalTickArraysOneJSON:
        return SupplementalTickArraysOneJSON(
            kind="SupplementalTickArraysOne",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "SupplementalTickArraysOne": {},
        }


@dataclass
class SupplementalTickArraysTwo:
    discriminator: typing.ClassVar = 8
    kind: typing.ClassVar = "SupplementalTickArraysTwo"

    @classmethod
    def to_json(cls) -> SupplementalTickArraysTwoJSON:
        return SupplementalTickArraysTwoJSON(
            kind="SupplementalTickArraysTwo",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "SupplementalTickArraysTwo": {},
        }


AccountsTypeKind = typing.Union[
    TransferHookA,
    TransferHookB,
    TransferHookReward,
    TransferHookInput,
    TransferHookIntermediate,
    TransferHookOutput,
    SupplementalTickArrays,
    SupplementalTickArraysOne,
    SupplementalTickArraysTwo,
]
AccountsTypeJSON = typing.Union[
    TransferHookAJSON,
    TransferHookBJSON,
    TransferHookRewardJSON,
    TransferHookInputJSON,
    TransferHookIntermediateJSON,
    TransferHookOutputJSON,
    SupplementalTickArraysJSON,
    SupplementalTickArraysOneJSON,
    SupplementalTickArraysTwoJSON,
]


def from_decoded(obj: dict) -> AccountsTypeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "TransferHookA" in obj:
        return TransferHookA()
    if "TransferHookB" in obj:
        return TransferHookB()
    if "TransferHookReward" in obj:
        return TransferHookReward()
    if "TransferHookInput" in obj:
        return TransferHookInput()
    if "TransferHookIntermediate" in obj:
        return TransferHookIntermediate()
    if "TransferHookOutput" in obj:
        return TransferHookOutput()
    if "SupplementalTickArrays" in obj:
        return SupplementalTickArrays()
    if "SupplementalTickArraysOne" in obj:
        return SupplementalTickArraysOne()
    if "SupplementalTickArraysTwo" in obj:
        return SupplementalTickArraysTwo()
    raise ValueError("Invalid enum object")


def from_json(obj: AccountsTypeJSON) -> AccountsTypeKind:
    if obj["kind"] == "TransferHookA":
        return TransferHookA()
    if obj["kind"] == "TransferHookB":
        return TransferHookB()
    if obj["kind"] == "TransferHookReward":
        return TransferHookReward()
    if obj["kind"] == "TransferHookInput":
        return TransferHookInput()
    if obj["kind"] == "TransferHookIntermediate":
        return TransferHookIntermediate()
    if obj["kind"] == "TransferHookOutput":
        return TransferHookOutput()
    if obj["kind"] == "SupplementalTickArrays":
        return SupplementalTickArrays()
    if obj["kind"] == "SupplementalTickArraysOne":
        return SupplementalTickArraysOne()
    if obj["kind"] == "SupplementalTickArraysTwo":
        return SupplementalTickArraysTwo()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "TransferHookA" / borsh.CStruct(),
    "TransferHookB" / borsh.CStruct(),
    "TransferHookReward" / borsh.CStruct(),
    "TransferHookInput" / borsh.CStruct(),
    "TransferHookIntermediate" / borsh.CStruct(),
    "TransferHookOutput" / borsh.CStruct(),
    "SupplementalTickArrays" / borsh.CStruct(),
    "SupplementalTickArraysOne" / borsh.CStruct(),
    "SupplementalTickArraysTwo" / borsh.CStruct(),
)
