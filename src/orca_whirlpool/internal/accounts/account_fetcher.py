from typing import List, Optional
from solders.account import Account
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from ..types.types import BlockTimestamp
from .types import WhirlpoolsConfig, FeeTier, Whirlpool, TickArray, Position, PositionBundle, MintInfo, AccountInfo
from .types import WhirlpoolsConfigExtension, TokenBadge
from .account_parser import AccountParser
from .keyed_account_converter import KeyedAccountConverter


BULK_FETCH_CHUNK_SIZE = 100


# https://github.com/orca-so/whirlpools/blob/7b9ec351e2048c5504ffc8894c0ec5a9e78dc113/sdk/src/network/public/fetcher.ts
class AccountFetcher:
    def __init__(self, connection: AsyncClient):
        self._connection = connection
        self._cache = {}

    async def _get(self, pubkey: Pubkey, parser, keyed_converter, refresh: bool, parse_with_program_id: bool = False):
        key = str(pubkey)
        if not refresh and key in self._cache:
            return self._cache[key]

        res = await self._connection.get_account_info(pubkey)
        if res.value is None:
            return None

        parsed = parser(res.value.data, res.value.owner) if parse_with_program_id else parser(res.value.data)
        if parsed is None:
            return None
        keyed = keyed_converter(pubkey, parsed)

        self._cache[key] = keyed
        return keyed

    async def _list(self, pubkeys: List[Pubkey], parser, keyed_converter, refresh: bool, parse_with_program_id: bool = False):
        fetch_needed = list(filter(lambda p: refresh or str(p) not in self._cache, pubkeys))

        if len(fetch_needed) > 0:
            fetched = await self._bulk_fetch(fetch_needed)
            for i in range(len(fetch_needed)):
                if fetched[i] is None:
                    continue
                parsed = parser(fetched[i].data, fetched[i].owner) if parse_with_program_id else parser(fetched[i].data)
                if parsed is None:
                    continue
                keyed = keyed_converter(fetch_needed[i], parsed)
                self._cache[str(fetch_needed[i])] = keyed

        return list(map(lambda p: self._cache.get(str(p)), pubkeys))

    async def _bulk_fetch(self, pubkeys: List[Pubkey]) -> List[Optional[Account]]:
        accounts = []
        for i in range(0, len(pubkeys), BULK_FETCH_CHUNK_SIZE):
            chunk = pubkeys[i:(i+BULK_FETCH_CHUNK_SIZE)]
            fetched = await self._connection.get_multiple_accounts(chunk)
            accounts.extend(fetched.value)
        return accounts

    async def get_whirlpool(self, pubkey: Pubkey, refresh: bool = False) -> Optional[Whirlpool]:
        return await self._get(pubkey, AccountParser.parse_whirlpool, KeyedAccountConverter.to_keyed_whirlpool, refresh)

    async def get_whirlpools_config(self, pubkey: Pubkey, refresh: bool = False) -> Optional[WhirlpoolsConfig]:
        return await self._get(pubkey, AccountParser.parse_whirlpools_config, KeyedAccountConverter.to_keyed_whirlpools_config, refresh)

    async def get_fee_tier(self, pubkey: Pubkey, refresh: bool = False) -> Optional[FeeTier]:
        return await self._get(pubkey, AccountParser.parse_fee_tier, KeyedAccountConverter.to_keyed_fee_tier, refresh)

    async def get_position(self, pubkey: Pubkey, refresh: bool = False) -> Optional[Position]:
        return await self._get(pubkey, AccountParser.parse_position, KeyedAccountConverter.to_keyed_position, refresh)

    async def get_tick_array(self, pubkey: Pubkey, refresh: bool = False) -> Optional[TickArray]:
        return await self._get(pubkey, AccountParser.parse_tick_array, KeyedAccountConverter.to_keyed_tick_array, refresh)

    async def get_position_bundle(self, pubkey: Pubkey, refresh: bool = False) -> Optional[PositionBundle]:
        return await self._get(pubkey, AccountParser.parse_position_bundle, KeyedAccountConverter.to_keyed_position_bundle, refresh)

    async def get_whirlpools_config_extension(self, pubkey: Pubkey, refresh: bool = False) -> Optional[WhirlpoolsConfigExtension]:
        return await self._get(pubkey, AccountParser.parse_whirlpools_config_extension, KeyedAccountConverter.to_keyed_whirlpools_config_extension, refresh)

    async def get_token_badge(self, pubkey: Pubkey, refresh: bool = False) -> Optional[TokenBadge]:
        return await self._get(pubkey, AccountParser.parse_token_badge, KeyedAccountConverter.to_keyed_token_badge, refresh)

    async def get_token_account(self, pubkey: Pubkey, refresh: bool = False) -> Optional[AccountInfo]:
        return await self._get(pubkey, AccountParser.parse_token_account, KeyedAccountConverter.to_keyed_token_account, refresh, True)

    async def get_token_mint(self, pubkey: Pubkey, refresh: bool = False) -> Optional[MintInfo]:
        return await self._get(pubkey, AccountParser.parse_token_mint, KeyedAccountConverter.to_keyed_token_mint, refresh, True)

    async def list_whirlpools(self, pubkeys: List[Pubkey], refresh: bool = False) -> List[Optional[Whirlpool]]:
        return await self._list(pubkeys, AccountParser.parse_whirlpool, KeyedAccountConverter.to_keyed_whirlpool, refresh)

    async def list_positions(self, pubkeys: List[Pubkey], refresh: bool = False) -> List[Optional[Position]]:
        return await self._list(pubkeys, AccountParser.parse_position, KeyedAccountConverter.to_keyed_position, refresh)

    async def list_tick_arrays(self, pubkeys: List[Pubkey], refresh: bool = False) -> List[Optional[TickArray]]:
        return await self._list(pubkeys, AccountParser.parse_tick_array, KeyedAccountConverter.to_keyed_tick_array, refresh)

    async def list_position_bundles(self, pubkeys: List[Pubkey], refresh: bool = False) -> List[Optional[PositionBundle]]:
        return await self._list(pubkeys, AccountParser.parse_position_bundle, KeyedAccountConverter.to_keyed_position_bundle, refresh)

    async def list_token_badges(self, pubkeys: List[Pubkey], refresh: bool = False) -> List[Optional[TokenBadge]]:
        return await self._list(pubkeys, AccountParser.parse_token_badge, KeyedAccountConverter.to_keyed_token_badge, refresh)

    async def list_token_accounts(self, pubkeys: List[Pubkey], refresh: bool = False) -> List[Optional[AccountInfo]]:
        return await self._list(pubkeys, AccountParser.parse_token_account, KeyedAccountConverter.to_keyed_token_account, refresh, True)

    async def list_token_mints(self, pubkeys: List[Pubkey], refresh: bool = False) -> List[Optional[MintInfo]]:
        return await self._list(pubkeys, AccountParser.parse_token_mint, KeyedAccountConverter.to_keyed_token_mint, refresh, True)

    async def get_latest_block_timestamp(self) -> BlockTimestamp:
        res1 = await self._connection.get_latest_blockhash()
        slot = res1.context.slot
        res2 = await self._connection.get_block_time(slot)
        timestamp = res2.value
        return BlockTimestamp(slot=slot, timestamp=timestamp)
