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


class WhirlpoolsConfigExtensionJSON(typing.TypedDict):
    whirlpools_config: str
    config_extension_authority: str
    token_badge_authority: str


@dataclass
class WhirlpoolsConfigExtension:
    discriminator: typing.ClassVar = b"\x02c\xd7\xa3\xf0\x1a\x99:"
    layout: typing.ClassVar = borsh.CStruct(
        "whirlpools_config" / BorshPubkey,
        "config_extension_authority" / BorshPubkey,
        "token_badge_authority" / BorshPubkey,
    )
    whirlpools_config: Pubkey
    config_extension_authority: Pubkey
    token_badge_authority: Pubkey

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["WhirlpoolsConfigExtension"]:
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
    ) -> typing.List[typing.Optional["WhirlpoolsConfigExtension"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["WhirlpoolsConfigExtension"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "WhirlpoolsConfigExtension":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = WhirlpoolsConfigExtension.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            whirlpools_config=dec.whirlpools_config,
            config_extension_authority=dec.config_extension_authority,
            token_badge_authority=dec.token_badge_authority,
        )

    def to_json(self) -> WhirlpoolsConfigExtensionJSON:
        return {
            "whirlpools_config": str(self.whirlpools_config),
            "config_extension_authority": str(self.config_extension_authority),
            "token_badge_authority": str(self.token_badge_authority),
        }

    @classmethod
    def from_json(
        cls, obj: WhirlpoolsConfigExtensionJSON
    ) -> "WhirlpoolsConfigExtension":
        return cls(
            whirlpools_config=Pubkey.from_string(obj["whirlpools_config"]),
            config_extension_authority=Pubkey.from_string(
                obj["config_extension_authority"]
            ),
            token_badge_authority=Pubkey.from_string(obj["token_badge_authority"]),
        )
