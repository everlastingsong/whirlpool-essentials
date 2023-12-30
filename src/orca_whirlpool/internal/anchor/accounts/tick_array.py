import typing
from dataclasses import dataclass
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from anchorpy.borsh_extension import BorshPubkey
from ..program_id import PROGRAM_ID
from .. import types


class TickArrayJSON(typing.TypedDict):
    start_tick_index: int
    ticks: list[types.tick.TickJSON]
    whirlpool: str


@dataclass
class TickArray:
    discriminator: typing.ClassVar = b"Ea\xbd\xben\x07B\xbb"
    layout: typing.ClassVar = borsh.CStruct(
        "start_tick_index" / borsh.I32,
        "ticks" / types.tick.Tick.layout[88],
        "whirlpool" / BorshPubkey,
    )
    start_tick_index: int
    ticks: list[types.tick.Tick]
    whirlpool: Pubkey

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["TickArray"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp.value
        if info is None:
            return None
        if info.owner != program_id:
            raise ValueError("Account does not belong to this program")
        bytes_data = info.data
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[Pubkey],
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.List[typing.Optional["TickArray"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["TickArray"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "TickArray":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = TickArray.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            start_tick_index=dec.start_tick_index,
            ticks=list(map(lambda item: types.tick.Tick.from_decoded(item), dec.ticks)),
            whirlpool=dec.whirlpool,
        )

    def to_json(self) -> TickArrayJSON:
        return {
            "start_tick_index": self.start_tick_index,
            "ticks": list(map(lambda item: item.to_json(), self.ticks)),
            "whirlpool": str(self.whirlpool),
        }

    @classmethod
    def from_json(cls, obj: TickArrayJSON) -> "TickArray":
        return cls(
            start_tick_index=obj["start_tick_index"],
            ticks=list(map(lambda item: types.tick.Tick.from_json(item), obj["ticks"])),
            whirlpool=Pubkey.from_string(obj["whirlpool"]),
        )
