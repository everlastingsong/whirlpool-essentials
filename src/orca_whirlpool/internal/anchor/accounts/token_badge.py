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


class TokenBadgeJSON(typing.TypedDict):
    whirlpools_config: str
    token_mint: str


@dataclass
class TokenBadge:
    discriminator: typing.ClassVar = b"t\xdb\xcc\xe5\xf9t\xff\x96"
    layout: typing.ClassVar = borsh.CStruct(
        "whirlpools_config" / BorshPubkey, "token_mint" / BorshPubkey
    )
    whirlpools_config: Pubkey
    token_mint: Pubkey

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["TokenBadge"]:
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
    ) -> typing.List[typing.Optional["TokenBadge"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["TokenBadge"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "TokenBadge":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = TokenBadge.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            whirlpools_config=dec.whirlpools_config,
            token_mint=dec.token_mint,
        )

    def to_json(self) -> TokenBadgeJSON:
        return {
            "whirlpools_config": str(self.whirlpools_config),
            "token_mint": str(self.token_mint),
        }

    @classmethod
    def from_json(cls, obj: TokenBadgeJSON) -> "TokenBadge":
        return cls(
            whirlpools_config=Pubkey.from_string(obj["whirlpools_config"]),
            token_mint=Pubkey.from_string(obj["token_mint"]),
        )
