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


class PositionBundleJSON(typing.TypedDict):
    position_bundle_mint: str
    position_bitmap: list[int]


@dataclass
class PositionBundle:
    discriminator: typing.ClassVar = b"\x81\xa9\xafA\xb9_ d"
    layout: typing.ClassVar = borsh.CStruct(
        "position_bundle_mint" / BorshPubkey, "position_bitmap" / borsh.U8[32]
    )
    position_bundle_mint: Pubkey
    position_bitmap: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["PositionBundle"]:
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
    ) -> typing.List[typing.Optional["PositionBundle"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["PositionBundle"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "PositionBundle":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = PositionBundle.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            position_bundle_mint=dec.position_bundle_mint,
            position_bitmap=dec.position_bitmap,
        )

    def to_json(self) -> PositionBundleJSON:
        return {
            "position_bundle_mint": str(self.position_bundle_mint),
            "position_bitmap": self.position_bitmap,
        }

    @classmethod
    def from_json(cls, obj: PositionBundleJSON) -> "PositionBundle":
        return cls(
            position_bundle_mint=Pubkey.from_string(obj["position_bundle_mint"]),
            position_bitmap=obj["position_bitmap"],
        )
