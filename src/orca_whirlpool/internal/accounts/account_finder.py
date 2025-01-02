from typing import List
from solders.pubkey import Pubkey
from solana.rpc.types import MemcmpOpts, TokenAccountOpts
from solana.rpc.async_api import AsyncClient
from spl.token.constants import TOKEN_PROGRAM_ID

from .account_fetcher import AccountFetcher
from ..constants import ACCOUNT_SIZE_WHIRLPOOL, ACCOUNT_SIZE_TICK_ARRAY, ACCOUNT_SIZE_POSITION, ACCOUNT_SIZE_FEE_TIER
from .types import Whirlpool, TickArray, Position, PositionBundle, FeeTier
from .account_parser import AccountParser
from .keyed_account_converter import KeyedAccountConverter
from ..utils.pda_util import PDAUtil
from ..utils.token_util import TokenUtil


class AccountFinder:
    def __init__(self, connection: AsyncClient):
        self._connection = connection

    async def find_whirlpools_by_whirlpools_config(self, program_id: Pubkey, whirlpools_config: Pubkey) -> List[Whirlpool]:
        accounts = (await self._connection.get_program_accounts(
            program_id,
            None,
            "base64",
            None,
            [ACCOUNT_SIZE_WHIRLPOOL, MemcmpOpts(8, str(whirlpools_config))]
        )).value

        return list(map(
            lambda a: KeyedAccountConverter.to_keyed_whirlpool(a.pubkey, AccountParser.parse_whirlpool(a.account.data)),
            accounts
        ))

    async def find_fee_tiers_by_whirlpools_config(self, program_id: Pubkey, whirlpools_config: Pubkey) -> List[FeeTier]:
        accounts = (await self._connection.get_program_accounts(
            program_id,
            None,
            "base64",
            None,
            [ACCOUNT_SIZE_FEE_TIER, MemcmpOpts(8, str(whirlpools_config))]
        )).value

        return list(map(
            lambda a: KeyedAccountConverter.to_keyed_fee_tier(a.pubkey, AccountParser.parse_fee_tier(a.account.data)),
            accounts
        ))

    async def find_tick_arrays_by_whirlpool(self, program_id: Pubkey, whirlpool: Pubkey) -> List[TickArray]:
        accounts = (await self._connection.get_program_accounts(
            program_id,
            None,
            "base64",
            None,
            [ACCOUNT_SIZE_TICK_ARRAY, MemcmpOpts(9956, str(whirlpool))]
        )).value

        return list(map(
            lambda a: KeyedAccountConverter.to_keyed_tick_array(a.pubkey, AccountParser.parse_tick_array(a.account.data)),
            accounts
        ))

    async def find_positions_by_whirlpool(self, program_id: Pubkey, whirlpool: Pubkey) -> List[Position]:
        accounts = (await self._connection.get_program_accounts(
            program_id,
            None,
            "base64",
            None,
            [ACCOUNT_SIZE_POSITION, MemcmpOpts(8, str(whirlpool))]
        )).value

        return list(map(
            lambda a: KeyedAccountConverter.to_keyed_position(a.pubkey, AccountParser.parse_position(a.account.data)),
            accounts
        ))

    async def find_positions_by_owner(self, program_id: Pubkey, owner: Pubkey, token_program_id: Pubkey) -> List[Position]:
        # list all token accounts
        accounts = (await self._connection.get_token_accounts_by_owner(
            owner,
            TokenAccountOpts(program_id=token_program_id, encoding="base64")
        )).value

        candidates = []
        for token_account in accounts:
            parsed = TokenUtil.deserialize_account(token_account.account.data, token_program_id)

            # maybe NFT
            if parsed.amount == 1:
                # derive position address
                position = PDAUtil.get_position(program_id, parsed.mint).pubkey
                candidates.append(position)

        fetcher = AccountFetcher(self._connection)
        fetched = await fetcher.list_positions(candidates, True)
        return list(filter(lambda a: a is not None, fetched))

    async def find_position_bundles_by_owner(self, program_id: Pubkey, owner: Pubkey) -> List[PositionBundle]:
        # list all token accounts
        accounts = (await self._connection.get_token_accounts_by_owner(
            owner,
            TokenAccountOpts(program_id=TOKEN_PROGRAM_ID, encoding="base64")
        )).value

        candidates = []
        for token_account in accounts:
            parsed = TokenUtil.deserialize_account(token_account.account.data, TOKEN_PROGRAM_ID)

            # maybe NFT
            if parsed.amount == 1:
                # derive position bundle address
                position = PDAUtil.get_position_bundle(program_id, parsed.mint).pubkey
                candidates.append(position)

        fetcher = AccountFetcher(self._connection)
        fetched = await fetcher.list_position_bundles(candidates, True)
        return list(filter(lambda a: a is not None, fetched))
