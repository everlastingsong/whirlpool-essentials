from typing import List, Optional
from solders.account import Account
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from orca_whirlpool.internal.types.types import BlockTimestamp
from orca_whirlpool.internal.accounts.types import WhirlpoolsConfig, FeeTier, Whirlpool, TickArray, Position, MintInfo, AccountInfo
from orca_whirlpool.internal.accounts.account_parser import AccountParser
from orca_whirlpool.internal.accounts.keyed_account_converter import KeyedAccountConverter


BULK_FETCH_CHUNK_SIZE = 100


# https://github.com/orca-so/whirlpools/blob/7b9ec351e2048c5504ffc8894c0ec5a9e78dc113/sdk/src/network/public/fetcher.ts
class SyncAccountFetcher:
    def __init__(self, connection: Client):
        self._connection = connection
        self._cache = {}

    def _get(self, pubkey: Pubkey, parser, keyed_converter, refresh: bool):
        key = str(pubkey)
        if not refresh and key in self._cache:
            return self._cache[key]

        res = self._connection.get_account_info(pubkey)
        if res.value is None:
            return None

        parsed = parser(res.value.data)
        if parsed is None:
            return None
        keyed = keyed_converter(pubkey, parsed)

        self._cache[key] = keyed
        return keyed

    def _list(self, pubkeys: List[Pubkey], parser, keyed_converter, refresh: bool):
        fetch_needed = list(filter(lambda p: refresh or str(p) not in self._cache, pubkeys))

        if len(fetch_needed) > 0:
            fetched = self._bulk_fetch(fetch_needed)
            for i in range(len(fetch_needed)):
                if fetched[i] is None:
                    continue
                parsed = parser(fetched[i].data)
                if parsed is None:
                    continue
                keyed = keyed_converter(fetch_needed[i], parsed)
                self._cache[str(fetch_needed[i])] = keyed

        return list(map(lambda p: self._cache.get(str(p)), pubkeys))

    def _bulk_fetch(self, pubkeys: List[Pubkey]) -> List[Optional[Account]]:
        accounts = []
        for i in range(0, len(pubkeys), BULK_FETCH_CHUNK_SIZE):
            chunk = pubkeys[i:(i+BULK_FETCH_CHUNK_SIZE)]
            fetched = self._connection.get_multiple_accounts(chunk)
            accounts.extend(fetched.value)
        return accounts

    def get_whirlpool(self, pubkey: Pubkey, refresh: bool = False) -> Optional[Whirlpool]:
        return self._get(pubkey, AccountParser.parse_whirlpool, KeyedAccountConverter.to_keyed_whirlpool, refresh)

    def get_whirlpools_config(self, pubkey: Pubkey, refresh: bool = False) -> Optional[WhirlpoolsConfig]:
        return self._get(pubkey, AccountParser.parse_whirlpools_config, KeyedAccountConverter.to_keyed_whirlpools_config, refresh)

    def get_fee_tier(self, pubkey: Pubkey, refresh: bool = False) -> Optional[FeeTier]:
        return self._get(pubkey, AccountParser.parse_fee_tier, KeyedAccountConverter.to_keyed_fee_tier, refresh)

    def get_position(self, pubkey: Pubkey, refresh: bool = False) -> Optional[Position]:
        return self._get(pubkey, AccountParser.parse_position, KeyedAccountConverter.to_keyed_position, refresh)

    def get_tick_array(self, pubkey: Pubkey, refresh: bool = False) -> Optional[TickArray]:
        return self._get(pubkey, AccountParser.parse_tick_array, KeyedAccountConverter.to_keyed_tick_array, refresh)

    def get_token_account(self, pubkey: Pubkey, refresh: bool = False) -> Optional[AccountInfo]:
        return self._get(pubkey, AccountParser.parse_token_account, KeyedAccountConverter.to_keyed_token_account, refresh)

    def get_token_mint(self, pubkey: Pubkey, refresh: bool = False) -> Optional[MintInfo]:
        return self._get(pubkey, AccountParser.parse_token_mint, KeyedAccountConverter.to_keyed_token_mint, refresh)

    def list_whirlpools(self, pubkeys: List[Pubkey], refresh: bool = False) -> List[Optional[Whirlpool]]:
        return self._list(pubkeys, AccountParser.parse_whirlpool, KeyedAccountConverter.to_keyed_whirlpool, refresh)

    def list_positions(self, pubkeys: List[Pubkey], refresh: bool = False) -> List[Optional[Position]]:
        return self._list(pubkeys, AccountParser.parse_position, KeyedAccountConverter.to_keyed_position, refresh)

    def list_tick_arrays(self, pubkeys: List[Pubkey], refresh: bool = False) -> List[Optional[TickArray]]:
        return self._list(pubkeys, AccountParser.parse_tick_array, KeyedAccountConverter.to_keyed_tick_array, refresh)

    def list_token_accounts(self, pubkeys: List[Pubkey], refresh: bool = False) -> List[Optional[AccountInfo]]:
        return self._list(pubkeys, AccountParser.parse_token_account, KeyedAccountConverter.to_keyed_token_account, refresh)

    def list_token_mints(self, pubkeys: List[Pubkey], refresh: bool = False) -> List[Optional[MintInfo]]:
        return self._list(pubkeys, AccountParser.parse_token_mint, KeyedAccountConverter.to_keyed_token_mint, refresh)

    def get_latest_block_timestamp(self) -> BlockTimestamp:
        res1 = self._connection.get_latest_blockhash()
        slot = res1.context.slot
        res2 = self._connection.get_block_time(slot)
        timestamp = res2.value
        return BlockTimestamp(slot=slot, timestamp=timestamp)
