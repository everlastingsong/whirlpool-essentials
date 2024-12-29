import unittest
import json
import pathlib
import base64
from typing import Optional, List
from solders.keypair import Keypair
from solders.account import Account
from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.rpc.responses import GetAccountInfoResp, GetMultipleAccountsResp, RpcResponseContext, GetLatestBlockhashResp, GetBlockTimeResp, GetMinimumBalanceForRentExemptionResp, RpcBlockhash
from solana.rpc.async_api import AsyncClient
from solana.rpc import types
from solana.rpc.core import Commitment

from orca_whirlpool.internal.accounts.account_fetcher import AccountFetcher
from orca_whirlpool.internal.utils.token_util import TokenUtil

ACCOUNT_JSON_FILES_DIR = "accounts"
ASYNC_CLIENT_STUB_BLOCK_SLOT = 160156384
ASYNC_CLIENT_STUB_BLOCK_TIMESTAMP = 1668008674
DUMMY_RPC = "http://localhost:8899"


def load_account_json(json_filepath: str) -> (Pubkey, Account):
    with open(json_filepath) as f:
        loaded = json.load(f)
    pubkey = Pubkey.from_string(loaded["pubkey"])
    account_json = loaded["account"]

    data_b64 = account_json["data"]
    data = base64.standard_b64decode(data_b64[0])
    lamports = int(account_json["lamports"])
    executable = bool(account_json["executable"])
    owner = Pubkey(bytes(Pubkey.from_string(account_json["owner"])))
    rent_epoch = int(account_json["rentEpoch"])

    return pubkey, Account(lamports, data, owner, executable, rent_epoch)


class AsyncClientStub(AsyncClient):
    def __init__(self, account_json_filenames: List[str], block_slot: int = 0, block_timestamp: int = 0):
        #super().__init__(DUMMY_RPC)

        # make cache from file
        dir = pathlib.Path(ACCOUNT_JSON_FILES_DIR)
        self._cache = {}
        for json_filename in account_json_filenames:
            json_filepath = dir / json_filename
            [pubkey, account] = load_account_json(str(json_filepath))
            self._cache[str(pubkey)] = account

        # slot/timestamp
        self.block_slot = block_slot
        self.block_timestamp = block_timestamp

        # init history list
        self.get_account_info_called = 0
        self.get_account_info_history = []
        self.get_multiple_accounts_called = 0
        self.get_multiple_accounts_history = []

    async def get_account_info(
        self,
        pubkey: Pubkey,
        commitment: Optional[Commitment] = None,
        encoding: str = "base64",
        data_slice: Optional[types.DataSliceOpts] = None,
    ) -> GetAccountInfoResp:
        self.get_account_info_called += 1
        self.get_account_info_history.append(pubkey)
        return GetAccountInfoResp(self._cache.get(str(pubkey)), RpcResponseContext(0))

    async def get_multiple_accounts(
        self,
        pubkeys: List[Pubkey],
        commitment: Optional[Commitment] = None,
        encoding: str = "base64",
        data_slice: Optional[types.DataSliceOpts] = None,
    ) -> GetMultipleAccountsResp:
        self.get_multiple_accounts_called += 1
        self.get_multiple_accounts_history.extend(pubkeys)
        return GetMultipleAccountsResp(
            [self._cache.get(str(p)) for p in pubkeys],
            RpcResponseContext(0)
        )

    async def get_latest_blockhash(self, commitment: Optional[Commitment] = None) -> GetLatestBlockhashResp:
        return GetLatestBlockhashResp(
            RpcBlockhash(Hash(bytes(Keypair().pubkey())), self.block_slot),
            RpcResponseContext(self.block_slot)
        )

    async def get_block_time(self, slot: int) -> GetBlockTimeResp:
        return GetBlockTimeResp(self.block_timestamp)

    async def get_minimum_balance_for_rent_exemption(
        self, usize: int, commitment: Optional[Commitment] = None
    ) -> GetMinimumBalanceForRentExemptionResp:
        return GetMinimumBalanceForRentExemptionResp(2039280)  # for TokenAccount


class AccountFetcherAndParserAndKeyedConverterTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_get_whirlpools_config_01(self):
        client = AsyncClientStub(["whirlpools_config.2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_whirlpools_config(Pubkey.from_string("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(Pubkey.from_string("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result.pubkey)
        self.assertEqual(Pubkey.from_string("3Pi4tc4SxZyKZivKxWnYfGNxeqFJJxPc8xRw1VnvXpbb"), result.fee_authority)
        self.assertEqual(Pubkey.from_string("3Pi4tc4SxZyKZivKxWnYfGNxeqFJJxPc8xRw1VnvXpbb"), result.collect_protocol_fees_authority)
        self.assertEqual(Pubkey.from_string("DjDsi34mSB66p2nhBL6YvhbcLtZbkGfNybFeLDjJqxJW"), result.reward_emissions_super_authority)
        self.assertEqual(300, result.default_protocol_fee_rate)

    async def test_get_whirlpools_config_extension_01(self):
        client = AsyncClientStub(["whirlpools_config_extension.777H5H3Tp9U11uRVRzFwM8BinfiakbaLT8vQpeuhvEiH.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_whirlpools_config_extension(Pubkey.from_string("777H5H3Tp9U11uRVRzFwM8BinfiakbaLT8vQpeuhvEiH"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(Pubkey.from_string("777H5H3Tp9U11uRVRzFwM8BinfiakbaLT8vQpeuhvEiH"), result.pubkey)
        self.assertEqual(Pubkey.from_string("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result.whirlpools_config)
        self.assertEqual(Pubkey.from_string("6BLTtBS9miUZruZtR9reTzp6ctGc4kVY4xrcxQwurYtw"), result.config_extension_authority)
        self.assertEqual(Pubkey.from_string("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6"), result.token_badge_authority)

    async def test_get_fee_tier_01(self):
        client = AsyncClientStub(["whirlpools_config_feetier64.HT55NVGVTjWmWLjV7BrSMPVZ7ppU8T2xE5nCAZ6YaGad.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_fee_tier(Pubkey.from_string("HT55NVGVTjWmWLjV7BrSMPVZ7ppU8T2xE5nCAZ6YaGad"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(Pubkey.from_string("HT55NVGVTjWmWLjV7BrSMPVZ7ppU8T2xE5nCAZ6YaGad"), result.pubkey)
        self.assertEqual(Pubkey.from_string("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result.whirlpools_config)
        self.assertEqual(64, result.tick_spacing)
        self.assertEqual(2000, result.default_fee_rate)  # old fee rate

    async def test_get_token_badge_01(self):
        client = AsyncClientStub(["token_badge_pyusd.HX5iftnCxhtu11ys3ZuWbvUqo7cyPYaVNZBrLL67Hrbm.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_token_badge(Pubkey.from_string("HX5iftnCxhtu11ys3ZuWbvUqo7cyPYaVNZBrLL67Hrbm"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(Pubkey.from_string("HX5iftnCxhtu11ys3ZuWbvUqo7cyPYaVNZBrLL67Hrbm"), result.pubkey)
        self.assertEqual(Pubkey.from_string("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result.whirlpools_config)
        self.assertEqual(Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo"), result.token_mint)

    async def test_get_whirlpool_01(self):
        client = AsyncClientStub(["sol_usdc_wp_whirlpool.HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_whirlpool(Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"), result.pubkey)
        self.assertEqual(Pubkey.from_string("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result.whirlpools_config)
        self.assertEqual([255], result.whirlpool_bump)
        self.assertEqual(64, result.tick_spacing)
        self.assertEqual([64, 0], result.tick_spacing_seed)
        self.assertEqual(2000, result.fee_rate)  # old fee rate
        self.assertEqual(300, result.protocol_fee_rate)
        self.assertEqual(179999872843830, result.liquidity)
        self.assertEqual(3706015876595606636, result.sqrt_price)
        self.assertEqual(-32101, result.tick_current_index)
        self.assertEqual(533835902873, result.protocol_fee_owed_a)
        self.assertEqual(25786963151, result.protocol_fee_owed_b)
        self.assertEqual(Pubkey.from_string("So11111111111111111111111111111111111111112"), result.token_mint_a)
        self.assertEqual(Pubkey.from_string("3YQm7ujtXWJU2e9jhp2QGHpnn1ShXn12QjvzMvDgabpX"), result.token_vault_a)
        self.assertEqual(5195114924723508514, result.fee_growth_global_a)
        self.assertEqual(Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"), result.token_mint_b)
        self.assertEqual(Pubkey.from_string("2JTw1fE2wz1SymWUQ7UqpVtrTuKjcd6mWwYwUJUCh2rq"), result.token_vault_b)
        self.assertEqual(219749538362201637, result.fee_growth_global_b)
        self.assertEqual(1659764580, result.reward_last_updated_timestamp)

        self.assertEqual(Pubkey.from_string("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE"), result.reward_infos[0].mint)
        self.assertEqual(Pubkey.from_string("2tU3tKvj7RBxEatryyMYTUxBoLSSWCQXsdv1X6yce4T2"), result.reward_infos[0].vault)
        self.assertEqual(Pubkey.from_string("DjDsi34mSB66p2nhBL6YvhbcLtZbkGfNybFeLDjJqxJW"), result.reward_infos[0].authority)
        self.assertEqual(0, result.reward_infos[0].emissions_per_second_x64)
        self.assertEqual(36063151640940598, result.reward_infos[0].growth_global_x64)

        self.assertEqual(Pubkey.from_string("11111111111111111111111111111111"), result.reward_infos[1].mint)
        self.assertEqual(Pubkey.from_string("11111111111111111111111111111111"), result.reward_infos[1].vault)
        self.assertEqual(Pubkey.from_string("3Pi4tc4SxZyKZivKxWnYfGNxeqFJJxPc8xRw1VnvXpbb"), result.reward_infos[1].authority)
        self.assertEqual(0, result.reward_infos[1].emissions_per_second_x64)
        self.assertEqual(0, result.reward_infos[1].growth_global_x64)

        self.assertEqual(Pubkey.from_string("11111111111111111111111111111111"), result.reward_infos[2].mint)
        self.assertEqual(Pubkey.from_string("11111111111111111111111111111111"), result.reward_infos[2].vault)
        self.assertEqual(Pubkey.from_string("3Pi4tc4SxZyKZivKxWnYfGNxeqFJJxPc8xRw1VnvXpbb"), result.reward_infos[2].authority)
        self.assertEqual(0, result.reward_infos[2].emissions_per_second_x64)
        self.assertEqual(0, result.reward_infos[2].growth_global_x64)

    async def test_get_tick_array_01(self):
        client = AsyncClientStub(["samo_usdc_wp_ta_n112640.CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_tick_array(Pubkey.from_string("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(Pubkey.from_string("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"), result.pubkey)
        self.assertEqual(Pubkey.from_string("9vqYJjDUFecLL2xPUC4Rc7hyCtZ6iJ4mDiVZX7aFXoAe"), result.whirlpool)
        self.assertEqual(-112640, result.start_tick_index)

        self.assertEqual(False, result.ticks[0].initialized)
        self.assertEqual(0, result.ticks[0].liquidity_net)
        self.assertEqual(0, result.ticks[0].liquidity_gross)
        self.assertEqual(0, result.ticks[0].fee_growth_outside_a)
        self.assertEqual(0, result.ticks[0].fee_growth_outside_b)
        self.assertEqual(0, result.ticks[0].reward_growths_outside[0])
        self.assertEqual(0, result.ticks[0].reward_growths_outside[1])
        self.assertEqual(0, result.ticks[0].reward_growths_outside[2])

        self.assertEqual(True, result.ticks[3].initialized)
        self.assertEqual(2413635782646, result.ticks[3].liquidity_net)
        self.assertEqual(2413635782646, result.ticks[3].liquidity_gross)
        self.assertEqual(139733337835095624306, result.ticks[3].fee_growth_outside_a)
        self.assertEqual(1074482472267776, result.ticks[3].fee_growth_outside_b)
        self.assertEqual(1106556054014923, result.ticks[3].reward_growths_outside[0])
        self.assertEqual(908724321447468561196, result.ticks[3].reward_growths_outside[1])
        self.assertEqual(0, result.ticks[3].reward_growths_outside[2])

        self.assertEqual(True, result.ticks[29].initialized)
        self.assertEqual(-16250028913342, result.ticks[29].liquidity_net)
        self.assertEqual(16250028913342, result.ticks[29].liquidity_gross)
        self.assertEqual(15852085550766700, result.ticks[29].fee_growth_outside_a)
        self.assertEqual(245214690465, result.ticks[29].fee_growth_outside_b)
        self.assertEqual(9556512961, result.ticks[29].reward_growths_outside[0])
        self.assertEqual(9564838191856183, result.ticks[29].reward_growths_outside[1])
        self.assertEqual(0, result.ticks[29].reward_growths_outside[2])

        self.assertEqual(False, result.ticks[87].initialized)
        self.assertEqual(0, result.ticks[87].liquidity_net)
        self.assertEqual(0, result.ticks[87].liquidity_gross)
        self.assertEqual(0, result.ticks[87].fee_growth_outside_a)
        self.assertEqual(0, result.ticks[87].fee_growth_outside_b)
        self.assertEqual(0, result.ticks[87].reward_growths_outside[0])
        self.assertEqual(0, result.ticks[87].reward_growths_outside[1])
        self.assertEqual(0, result.ticks[87].reward_growths_outside[2])

    async def test_get_position_01(self):
        client = AsyncClientStub(["sol_usdc_wp_position.5j3szbi2vnydYoyALNgttPD9YhCNwshUGkhzmzaP4WF7.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_position(Pubkey.from_string("5j3szbi2vnydYoyALNgttPD9YhCNwshUGkhzmzaP4WF7"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(Pubkey.from_string("5j3szbi2vnydYoyALNgttPD9YhCNwshUGkhzmzaP4WF7"), result.pubkey)
        self.assertEqual(Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"), result.whirlpool)
        self.assertEqual(Pubkey.from_string("AuB2UXTArEWXCUaNxYPCGKoigjD6cX5BMbXPs8qsEe39"), result.position_mint)
        self.assertEqual(50496375, result.liquidity)
        self.assertEqual(-33472, result.tick_lower_index)
        self.assertEqual(-30976, result.tick_upper_index)
        self.assertEqual(1369819610820621351, result.fee_growth_checkpoint_a)
        self.assertEqual(1199710, result.fee_owed_a)
        self.assertEqual(37791207404443253, result.fee_growth_checkpoint_b)
        self.assertEqual(48310, result.fee_owed_b)

        self.assertEqual(340282366920938463463361188517146862200, result.reward_infos[0].growth_inside_checkpoint)
        self.assertEqual(0, result.reward_infos[0].amount_owed)

        self.assertEqual(0, result.reward_infos[1].growth_inside_checkpoint)
        self.assertEqual(0, result.reward_infos[1].amount_owed)

        self.assertEqual(0, result.reward_infos[2].growth_inside_checkpoint)
        self.assertEqual(0, result.reward_infos[2].amount_owed)

    async def test_get_token_mint_01(self):
        # Token Program
        client = AsyncClientStub(["token_orca.orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_token_mint(Pubkey.from_string("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(Pubkey.from_string("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE"), result.pubkey)
        self.assertEqual(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), result.token_program_id)
        self.assertEqual(Pubkey.from_string("8DzsCSvbvBDYxGB4ytNF698zi6Dyo9dUBVRNjZQFHSUt"), result.mint_authority)
        self.assertEqual(99999990272788, result.supply)
        self.assertEqual(6, result.decimals)
        self.assertEqual(True, result.is_initialized)
        self.assertIsNone(result.freeze_authority)  # no freeze authority
        self.assertEqual(0, len(result.tlv_data))

    async def test_get_token_mint_02(self):
        # Token-2022 Program
        client = AsyncClientStub(["token_2022_pyusd.2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_token_mint(Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo"), result.pubkey)
        self.assertEqual(Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"), result.token_program_id)
        self.assertEqual(Pubkey.from_string("22mKJkKjGEQ3rampp5YKaSsaYZ52BUkcnUN6evXGsXzz"), result.mint_authority)
        self.assertEqual(177784511063664, result.supply)
        self.assertEqual(6, result.decimals)
        self.assertEqual(True, result.is_initialized)
        self.assertEqual(Pubkey.from_string("2apBGMsS6ti9RyF5TwQTDswXBWskiJP2LD4cUEDqYJjk"), result.freeze_authority)
        self.assertEqual(700, len(result.tlv_data))
        self.assertEqual(bytes([0x03, 0x00, 0x20, 0x00]), result.tlv_data[0:4])

    async def test_get_token_account_01(self):
        # Token Program
        client = AsyncClientStub(["user_ata_orca.7B8yNHX62NLvRswD86ttbGcV5TYxUsDNxEg2ZRMZLPRt.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_token_account(Pubkey.from_string("7B8yNHX62NLvRswD86ttbGcV5TYxUsDNxEg2ZRMZLPRt"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(Pubkey.from_string("7B8yNHX62NLvRswD86ttbGcV5TYxUsDNxEg2ZRMZLPRt"), result.pubkey)
        self.assertEqual(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), result.token_program_id)
        self.assertEqual(Pubkey.from_string("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE"), result.mint)
        self.assertEqual(Pubkey.from_string("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6"), result.owner)
        self.assertEqual(58875, result.amount)
        self.assertIsNone(result.delegate)  # no delegation
        self.assertEqual(False, result.is_native)
        self.assertEqual(0, result.delegated_amount)
        self.assertIsNone(result.close_authority)  # no celose authority
        self.assertEqual(0, len(result.tlv_data))

    async def test_get_token_account_02(self):
        # Token-2022 Program
        client = AsyncClientStub(["user_ata_2022_pyusd.2A7Cc48jwWWoixM5CWquQKEqk9KNQvY2Xw3WJbBRc6Ei.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_token_account(Pubkey.from_string("2A7Cc48jwWWoixM5CWquQKEqk9KNQvY2Xw3WJbBRc6Ei"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(Pubkey.from_string("2A7Cc48jwWWoixM5CWquQKEqk9KNQvY2Xw3WJbBRc6Ei"), result.pubkey)
        self.assertEqual(Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"), result.token_program_id)
        self.assertEqual(Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo"), result.mint)
        self.assertEqual(Pubkey.from_string("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6"), result.owner)
        self.assertEqual(849007, result.amount)
        self.assertIsNone(result.delegate)  # no delegation
        self.assertEqual(False, result.is_native)
        self.assertEqual(0, result.delegated_amount)
        self.assertIsNone(result.close_authority)  # no celose authority
        self.assertEqual(21, len(result.tlv_data))
        self.assertEqual(bytes([0x07, 0x00, 0x00, 0x00, 0x02, 0x00, 0x08, 0x00]), result.tlv_data[0:8])

    async def test_list_token_mints_01(self):
        # Token Program
        client = AsyncClientStub([
            "token_orca.orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE.json",
            "token_samo.7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU.json",
            "token_usdc.EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v.json",
        ])
        fetcher = AccountFetcher(client)
        result = await fetcher.list_token_mints([
            Pubkey.from_string("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE"),
            Pubkey.from_string("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"),
            Pubkey.from_string("mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So"),
            Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(4, len(client.get_multiple_accounts_history))

        self.assertEqual(Pubkey.from_string("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE"), result[0].pubkey)
        self.assertEqual(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), result[0].token_program_id)
        self.assertEqual(Pubkey.from_string("8DzsCSvbvBDYxGB4ytNF698zi6Dyo9dUBVRNjZQFHSUt"), result[0].mint_authority)
        self.assertEqual(0, len(result[0].tlv_data))
        self.assertEqual(Pubkey.from_string("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"), result[1].pubkey)
        self.assertEqual(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), result[1].token_program_id)
        self.assertIsNone(result[1].mint_authority)  # no mint authority
        self.assertEqual(0, len(result[1].tlv_data))
        self.assertIsNone(result[2])
        self.assertEqual(Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"), result[3].pubkey)
        self.assertEqual(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), result[3].token_program_id)
        self.assertEqual(Pubkey.from_string("2wmVCSfPxGPjrnMMn7rchp4uaeoTqN39mXFC2zhPdri9"), result[3].mint_authority)
        self.assertEqual(0, len(result[3].tlv_data))

    async def test_list_token_mints_02(self):
        # Token-2022 Program
        client = AsyncClientStub([
            "token_2022_pyusd.2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo.json",
            "token_2022_susd.susdabGDNbhrnCa6ncrYo81u4s9GM8ecK2UwMyZiq4X.json",
        ])
        fetcher = AccountFetcher(client)
        result = await fetcher.list_token_mints([
            Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo"),
            Pubkey.from_string("CKfatsPMUf8SkiURsDXs7eK6GWb4Jsd6UDbs7twMCWxo"),
            Pubkey.from_string("susdabGDNbhrnCa6ncrYo81u4s9GM8ecK2UwMyZiq4X"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(3, len(client.get_multiple_accounts_history))

        self.assertEqual(Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo"), result[0].pubkey)
        self.assertEqual(Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"), result[0].token_program_id)
        self.assertEqual(Pubkey.from_string("22mKJkKjGEQ3rampp5YKaSsaYZ52BUkcnUN6evXGsXzz"), result[0].mint_authority)
        self.assertEqual(700, len(result[0].tlv_data))
        self.assertEqual(bytes([0x03, 0x00, 0x20, 0x00]), result[0].tlv_data[0:4])
        self.assertIsNone(result[1])
        self.assertEqual(Pubkey.from_string("susdabGDNbhrnCa6ncrYo81u4s9GM8ecK2UwMyZiq4X"), result[2].pubkey)
        self.assertEqual(Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"), result[2].token_program_id)
        self.assertEqual(Pubkey.from_string("FhVcYNEe58SMtxpZGnTu2kpYJrTu2vwCZDGpPLqbd2yG"), result[2].mint_authority)
        self.assertEqual(271, len(result[2].tlv_data))
        self.assertEqual(bytes([0x12, 0x00, 0x40, 0x00]), result[2].tlv_data[0:4])

    async def test_list_token_mints_03(self):
        # Token Program & Token-2022 Program
        client = AsyncClientStub([
            "token_orca.orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE.json",
            "token_samo.7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU.json",
            "token_2022_pyusd.2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo.json",
            "token_2022_susd.susdabGDNbhrnCa6ncrYo81u4s9GM8ecK2UwMyZiq4X.json",
        ])
        fetcher = AccountFetcher(client)
        result = await fetcher.list_token_mints([
            Pubkey.from_string("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE"),
            Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo"),
            Pubkey.from_string("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"),
            Pubkey.from_string("susdabGDNbhrnCa6ncrYo81u4s9GM8ecK2UwMyZiq4X"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(4, len(client.get_multiple_accounts_history))

        self.assertEqual(Pubkey.from_string("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE"), result[0].pubkey)
        self.assertEqual(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), result[0].token_program_id)
        self.assertEqual(Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo"), result[1].pubkey)
        self.assertEqual(Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"), result[1].token_program_id)
        self.assertEqual(Pubkey.from_string("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"), result[2].pubkey)
        self.assertEqual(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), result[2].token_program_id)
        self.assertEqual(Pubkey.from_string("susdabGDNbhrnCa6ncrYo81u4s9GM8ecK2UwMyZiq4X"), result[3].pubkey)
        self.assertEqual(Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"), result[3].token_program_id)

    async def test_list_token_accounts_01(self):
        # Token Program
        client = AsyncClientStub([
            "samo_usdc_wp_vault_a.3xxgYc3jXPdjqpMdrRyKtcddh4ZdtqpaN33fwaWJ2Wbh.json",
            "samo_usdc_wp_vault_b.8xKCx3SGwWR6BUr9mZFm3xwZmCVMuLjXn9iLEU6784FS.json",
            "sol_usdc_wp_vault_a.3YQm7ujtXWJU2e9jhp2QGHpnn1ShXn12QjvzMvDgabpX.json",
            "sol_usdc_wp_vault_b.2JTw1fE2wz1SymWUQ7UqpVtrTuKjcd6mWwYwUJUCh2rq.json",
        ])
        fetcher = AccountFetcher(client)
        result = await fetcher.list_token_accounts([
            Pubkey.from_string("3xxgYc3jXPdjqpMdrRyKtcddh4ZdtqpaN33fwaWJ2Wbh"),
            Pubkey.from_string("8xKCx3SGwWR6BUr9mZFm3xwZmCVMuLjXn9iLEU6784FS"),
            Pubkey.from_string("6dM4iMgSei6zF9y3sqdgSJ2xwNXML5wk5QKhV4DqJPhu"),
            Pubkey.from_string("3YQm7ujtXWJU2e9jhp2QGHpnn1ShXn12QjvzMvDgabpX"),
            Pubkey.from_string("2JTw1fE2wz1SymWUQ7UqpVtrTuKjcd6mWwYwUJUCh2rq"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(5, len(client.get_multiple_accounts_history))

        self.assertEqual(Pubkey.from_string("3xxgYc3jXPdjqpMdrRyKtcddh4ZdtqpaN33fwaWJ2Wbh"), result[0].pubkey)
        self.assertEqual(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), result[0].token_program_id)
        self.assertEqual(Pubkey.from_string("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"), result[0].mint)
        self.assertEqual(0, len(result[0].tlv_data))
        self.assertEqual(Pubkey.from_string("8xKCx3SGwWR6BUr9mZFm3xwZmCVMuLjXn9iLEU6784FS"), result[1].pubkey)
        self.assertEqual(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), result[1].token_program_id)
        self.assertEqual(Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"), result[1].mint)
        self.assertEqual(0, len(result[1].tlv_data))
        self.assertIsNone(result[2])
        self.assertEqual(Pubkey.from_string("3YQm7ujtXWJU2e9jhp2QGHpnn1ShXn12QjvzMvDgabpX"), result[3].pubkey)
        self.assertEqual(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), result[3].token_program_id)
        self.assertEqual(Pubkey.from_string("So11111111111111111111111111111111111111112"), result[3].mint)
        self.assertEqual(0, len(result[3].tlv_data))
        self.assertEqual(Pubkey.from_string("2JTw1fE2wz1SymWUQ7UqpVtrTuKjcd6mWwYwUJUCh2rq"), result[4].pubkey)
        self.assertEqual(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), result[4].token_program_id)
        self.assertEqual(Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"), result[4].mint)
        self.assertEqual(0, len(result[4].tlv_data))

    async def test_list_token_accounts_02(self):
        # Token-2022 Program
        client = AsyncClientStub([
            "user_ata_2022_pyusd.2A7Cc48jwWWoixM5CWquQKEqk9KNQvY2Xw3WJbBRc6Ei.json",
            "user_ata_2022_susd.6nC3JjFC3fQx9HhHB27VzkdDMK6k38H9a2cNsZgk8yUy.json",
        ])
        fetcher = AccountFetcher(client)
        result = await fetcher.list_token_accounts([
            Pubkey.from_string("2A7Cc48jwWWoixM5CWquQKEqk9KNQvY2Xw3WJbBRc6Ei"),
            Pubkey.from_string("EeF6oBy6AQiBJoRx5xiRNxa6cmpQE3ayVagj28QFZuyg"),
            Pubkey.from_string("6nC3JjFC3fQx9HhHB27VzkdDMK6k38H9a2cNsZgk8yUy"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(3, len(client.get_multiple_accounts_history))

        self.assertEqual(Pubkey.from_string("2A7Cc48jwWWoixM5CWquQKEqk9KNQvY2Xw3WJbBRc6Ei"), result[0].pubkey)
        self.assertEqual(Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"), result[0].token_program_id)
        self.assertEqual(Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo"), result[0].mint)
        self.assertEqual(21, len(result[0].tlv_data))
        self.assertEqual(bytes([0x07, 0x00, 0x00, 0x00, 0x02, 0x00, 0x08, 0x00]), result[0].tlv_data[0:8])
        self.assertIsNone(result[1])
        self.assertEqual(Pubkey.from_string("6nC3JjFC3fQx9HhHB27VzkdDMK6k38H9a2cNsZgk8yUy"), result[2].pubkey)
        self.assertEqual(Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"), result[2].token_program_id)
        self.assertEqual(Pubkey.from_string("susdabGDNbhrnCa6ncrYo81u4s9GM8ecK2UwMyZiq4X"), result[2].mint)
        self.assertEqual(4, len(result[2].tlv_data))
        self.assertEqual(bytes([0x07, 0x00, 0x00, 0x00]), result[2].tlv_data[0:4])

    async def test_list_token_accounts_03(self):
        # Token Program & Token-2022 Program
        client = AsyncClientStub([
            "samo_usdc_wp_vault_b.8xKCx3SGwWR6BUr9mZFm3xwZmCVMuLjXn9iLEU6784FS.json",
            "sol_usdc_wp_vault_a.3YQm7ujtXWJU2e9jhp2QGHpnn1ShXn12QjvzMvDgabpX.json",
            "user_ata_2022_pyusd.2A7Cc48jwWWoixM5CWquQKEqk9KNQvY2Xw3WJbBRc6Ei.json",
            "user_ata_2022_susd.6nC3JjFC3fQx9HhHB27VzkdDMK6k38H9a2cNsZgk8yUy.json",
        ])
        fetcher = AccountFetcher(client)
        result = await fetcher.list_token_accounts([
            Pubkey.from_string("8xKCx3SGwWR6BUr9mZFm3xwZmCVMuLjXn9iLEU6784FS"),
            Pubkey.from_string("2A7Cc48jwWWoixM5CWquQKEqk9KNQvY2Xw3WJbBRc6Ei"),
            Pubkey.from_string("3YQm7ujtXWJU2e9jhp2QGHpnn1ShXn12QjvzMvDgabpX"),
            Pubkey.from_string("6nC3JjFC3fQx9HhHB27VzkdDMK6k38H9a2cNsZgk8yUy"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(4, len(client.get_multiple_accounts_history))

        self.assertEqual(Pubkey.from_string("8xKCx3SGwWR6BUr9mZFm3xwZmCVMuLjXn9iLEU6784FS"), result[0].pubkey)
        self.assertEqual(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), result[0].token_program_id)
        self.assertEqual(Pubkey.from_string("2A7Cc48jwWWoixM5CWquQKEqk9KNQvY2Xw3WJbBRc6Ei"), result[1].pubkey)
        self.assertEqual(Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"), result[1].token_program_id)
        self.assertEqual(Pubkey.from_string("3YQm7ujtXWJU2e9jhp2QGHpnn1ShXn12QjvzMvDgabpX"), result[2].pubkey)
        self.assertEqual(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), result[2].token_program_id)
        self.assertEqual(Pubkey.from_string("6nC3JjFC3fQx9HhHB27VzkdDMK6k38H9a2cNsZgk8yUy"), result[3].pubkey)
        self.assertEqual(Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"), result[3].token_program_id)

    async def test_list_whirlpools_01(self):
        client = AsyncClientStub([
            "sol_usdc_wp_whirlpool.HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ.json",
            "samo_usdc_wp_whirlpool.9vqYJjDUFecLL2xPUC4Rc7hyCtZ6iJ4mDiVZX7aFXoAe.json",
        ])
        fetcher = AccountFetcher(client)
        result = await fetcher.list_whirlpools([
            Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"),
            Pubkey.from_string("9vqYJjDUFecLL2xPUC4Rc7hyCtZ6iJ4mDiVZX7aFXoAe"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(2, len(client.get_multiple_accounts_history))

        self.assertEqual(Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"), result[0].pubkey)
        self.assertEqual(Pubkey.from_string("So11111111111111111111111111111111111111112"), result[0].token_mint_a)
        self.assertEqual(Pubkey.from_string("9vqYJjDUFecLL2xPUC4Rc7hyCtZ6iJ4mDiVZX7aFXoAe"), result[1].pubkey)
        self.assertEqual(Pubkey.from_string("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"), result[1].token_mint_a)

    async def test_list_positions_01(self):
        client = AsyncClientStub([
            "samo_usdc_wp_position.B66pRzGcKMmxRJ16KMkJMJoQWWhmyk4na4DPcv6X5ZRD.json",
            "sol_usdc_wp_position.5j3szbi2vnydYoyALNgttPD9YhCNwshUGkhzmzaP4WF7.json",
        ])
        fetcher = AccountFetcher(client)
        result = await fetcher.list_positions([
            Pubkey.from_string("B66pRzGcKMmxRJ16KMkJMJoQWWhmyk4na4DPcv6X5ZRD"),
            Pubkey.from_string("5j3szbi2vnydYoyALNgttPD9YhCNwshUGkhzmzaP4WF7"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(2, len(client.get_multiple_accounts_history))

        self.assertEqual(Pubkey.from_string("B66pRzGcKMmxRJ16KMkJMJoQWWhmyk4na4DPcv6X5ZRD"), result[0].pubkey)
        self.assertEqual(Pubkey.from_string("9vqYJjDUFecLL2xPUC4Rc7hyCtZ6iJ4mDiVZX7aFXoAe"), result[0].whirlpool)
        self.assertEqual(Pubkey.from_string("5j3szbi2vnydYoyALNgttPD9YhCNwshUGkhzmzaP4WF7"), result[1].pubkey)
        self.assertEqual(Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"), result[1].whirlpool)

    async def test_list_tick_arrays_01(self):
        client = AsyncClientStub([
            "samo_usdc_wp_ta_n95744.C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH.json",
            "samo_usdc_wp_ta_n101376.HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF.json",
            "samo_usdc_wp_ta_n107008.EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ.json",
            "samo_usdc_wp_ta_n112640.CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH.json",
            "samo_usdc_wp_ta_n118272.4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G.json",
            "samo_usdc_wp_ta_n123904.Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT.json",
            "samo_usdc_wp_ta_n129536.ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq.json",
        ])
        fetcher = AccountFetcher(client)
        result = await fetcher.list_tick_arrays([
            Pubkey.from_string("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            Pubkey.from_string("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            Pubkey.from_string("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            Pubkey.from_string("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            Pubkey.from_string("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            Pubkey.from_string("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            Pubkey.from_string("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(7, len(client.get_multiple_accounts_history))

        self.assertEqual(Pubkey.from_string("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"), result[0].pubkey)
        self.assertEqual(Pubkey.from_string("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"), result[1].pubkey)
        self.assertEqual(Pubkey.from_string("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"), result[2].pubkey)
        self.assertEqual(Pubkey.from_string("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"), result[3].pubkey)
        self.assertEqual(Pubkey.from_string("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"), result[4].pubkey)
        self.assertEqual(Pubkey.from_string("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"), result[5].pubkey)
        self.assertEqual(Pubkey.from_string("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"), result[6].pubkey)

        self.assertEqual(-95744, result[0].start_tick_index)
        self.assertEqual(-101376, result[1].start_tick_index)
        self.assertEqual(-107008, result[2].start_tick_index)
        self.assertEqual(-112640, result[3].start_tick_index)
        self.assertEqual(-118272, result[4].start_tick_index)
        self.assertEqual(-123904, result[5].start_tick_index)
        self.assertEqual(-129536, result[6].start_tick_index)

    async def test_list_token_badge_01(self):
        client = AsyncClientStub([
            "token_badge_pyusd.HX5iftnCxhtu11ys3ZuWbvUqo7cyPYaVNZBrLL67Hrbm.json",
            "token_badge_susd.5Me4K3Ck1dr8CzS3mKx2pMrMLnJoazdBqsXzW8kbQGdw.json",
        ])
        fetcher = AccountFetcher(client)
        result = await fetcher.list_token_badges([
            Pubkey.from_string("HX5iftnCxhtu11ys3ZuWbvUqo7cyPYaVNZBrLL67Hrbm"),
            Pubkey.from_string("GExmehuh3gJacobvuYPqxmptNuyGoSbbz4oS5VJwUMjt"),
            Pubkey.from_string("5Me4K3Ck1dr8CzS3mKx2pMrMLnJoazdBqsXzW8kbQGdw"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(3, len(client.get_multiple_accounts_history))

        self.assertEqual(Pubkey.from_string("HX5iftnCxhtu11ys3ZuWbvUqo7cyPYaVNZBrLL67Hrbm"), result[0].pubkey)
        self.assertEqual(Pubkey.from_string("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result[0].whirlpools_config)
        self.assertEqual(Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo"), result[0].token_mint)
        self.assertIsNone(result[1])
        self.assertEqual(Pubkey.from_string("5Me4K3Ck1dr8CzS3mKx2pMrMLnJoazdBqsXzW8kbQGdw"), result[2].pubkey)
        self.assertEqual(Pubkey.from_string("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result[2].whirlpools_config)
        self.assertEqual(Pubkey.from_string("susdabGDNbhrnCa6ncrYo81u4s9GM8ecK2UwMyZiq4X"), result[2].token_mint)

    async def test_cache_get_01(self):
        client = AsyncClientStub(["sol_usdc_wp_whirlpool.HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ.json"])
        fetcher = AccountFetcher(client)

        result1 = await fetcher.get_whirlpool(Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"))
        self.assertEqual(Pubkey.from_string("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result1.whirlpools_config)
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        result2 = await fetcher.get_whirlpool(Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"))
        self.assertEqual(Pubkey.from_string("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result2.whirlpools_config)
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        result3 = await fetcher.get_whirlpool(Pubkey.from_string("2AEWSvUds1wsufnsDPCXjFsJCMJH5SNNm7fSF4kxys9a"))
        self.assertIsNone(result3)
        self.assertEqual(2, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        result4 = await fetcher.get_whirlpool(Pubkey.from_string("2AEWSvUds1wsufnsDPCXjFsJCMJH5SNNm7fSF4kxys9a"))
        self.assertIsNone(result4)
        self.assertEqual(3, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        result5 = await fetcher.get_whirlpool(Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"))
        self.assertEqual(Pubkey.from_string("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result5.whirlpools_config)
        self.assertEqual(3, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        result6 = await fetcher.get_whirlpool(Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"), True)
        self.assertEqual(Pubkey.from_string("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result6.whirlpools_config)
        self.assertEqual(4, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

    async def test_cache_list_01(self):
        client = AsyncClientStub([
            "samo_usdc_wp_ta_n95744.C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH.json",
            "samo_usdc_wp_ta_n101376.HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF.json",
            "samo_usdc_wp_ta_n107008.EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ.json",
            "samo_usdc_wp_ta_n112640.CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH.json",
            "samo_usdc_wp_ta_n118272.4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G.json",
            "samo_usdc_wp_ta_n123904.Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT.json",
            "samo_usdc_wp_ta_n129536.ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq.json",
        ])
        fetcher = AccountFetcher(client)
        result1 = await fetcher.list_tick_arrays([
            Pubkey.from_string("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            Pubkey.from_string("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            Pubkey.from_string("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            # Pubkey.from_string("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            # Pubkey.from_string("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            # Pubkey.from_string("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            # Pubkey.from_string("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
        ])
        self.assertEqual(-95744, result1[0].start_tick_index)
        self.assertEqual(-101376, result1[1].start_tick_index)
        self.assertEqual(-107008, result1[2].start_tick_index)
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(3, len(client.get_multiple_accounts_history))

        result2 = await fetcher.list_tick_arrays([
            Pubkey.from_string("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            Pubkey.from_string("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            Pubkey.from_string("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            # Pubkey.from_string("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            # Pubkey.from_string("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            # Pubkey.from_string("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            # Pubkey.from_string("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
        ])
        self.assertEqual(-95744, result2[0].start_tick_index)
        self.assertEqual(-101376, result2[1].start_tick_index)
        self.assertEqual(-107008, result2[2].start_tick_index)
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(3, len(client.get_multiple_accounts_history))

        result3 = await fetcher.list_tick_arrays([
            Pubkey.from_string("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            Pubkey.from_string("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            # Pubkey.from_string("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            Pubkey.from_string("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            Pubkey.from_string("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            # Pubkey.from_string("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            # Pubkey.from_string("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
        ])
        self.assertEqual(-95744, result3[0].start_tick_index)
        self.assertEqual(-101376, result3[1].start_tick_index)
        self.assertEqual(-112640, result3[2].start_tick_index)
        self.assertEqual(-118272, result3[3].start_tick_index)
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(2, client.get_multiple_accounts_called)
        self.assertEqual(5, len(client.get_multiple_accounts_history))

        result4 = await fetcher.list_tick_arrays([
            Pubkey.from_string("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            Pubkey.from_string("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            # Pubkey.from_string("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            Pubkey.from_string("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            Pubkey.from_string("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            # Pubkey.from_string("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            # Pubkey.from_string("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
        ], True)
        self.assertEqual(-95744, result4[0].start_tick_index)
        self.assertEqual(-101376, result4[1].start_tick_index)
        self.assertEqual(-112640, result4[2].start_tick_index)
        self.assertEqual(-118272, result4[3].start_tick_index)
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(3, client.get_multiple_accounts_called)
        self.assertEqual(9, len(client.get_multiple_accounts_history))

        result5 = await fetcher.get_tick_array(Pubkey.from_string("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"))
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(3, client.get_multiple_accounts_called)
        self.assertEqual(9, len(client.get_multiple_accounts_history))

        result6 = await fetcher.get_tick_array(Pubkey.from_string("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"))
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(3, client.get_multiple_accounts_called)
        self.assertEqual(9, len(client.get_multiple_accounts_history))

        result7 = await fetcher.get_tick_array(Pubkey.from_string("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(3, client.get_multiple_accounts_called)
        self.assertEqual(9, len(client.get_multiple_accounts_history))

        result8 = await fetcher.get_tick_array(Pubkey.from_string("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"))
        self.assertEqual(2, client.get_account_info_called)
        self.assertEqual(3, client.get_multiple_accounts_called)
        self.assertEqual(9, len(client.get_multiple_accounts_history))

        result9 = await fetcher.list_tick_arrays([
            Pubkey.from_string("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            Pubkey.from_string("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            Pubkey.from_string("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            Pubkey.from_string("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            Pubkey.from_string("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            Pubkey.from_string("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            Pubkey.from_string("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
        ], False)
        self.assertEqual(2, client.get_account_info_called)
        self.assertEqual(3, client.get_multiple_accounts_called)
        self.assertEqual(9, len(client.get_multiple_accounts_history))

        result10 = await fetcher.get_tick_array(Pubkey.from_string("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"), True)
        self.assertEqual(3, client.get_account_info_called)
        self.assertEqual(3, client.get_multiple_accounts_called)
        self.assertEqual(9, len(client.get_multiple_accounts_history))

    async def test_cache_list_02(self):
        client = AsyncClientStub([
            "samo_usdc_wp_ta_n95744.C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH.json",
            "samo_usdc_wp_ta_n101376.HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF.json",
            "samo_usdc_wp_ta_n107008.EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ.json",
            "samo_usdc_wp_ta_n112640.CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH.json",
            # "samo_usdc_wp_ta_n118272.4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G.json",
            # "samo_usdc_wp_ta_n123904.Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT.json",
            # "samo_usdc_wp_ta_n129536.ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq.json",
        ])
        fetcher = AccountFetcher(client)
        result1 = await fetcher.list_tick_arrays([
            Pubkey.from_string("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            Pubkey.from_string("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            Pubkey.from_string("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            Pubkey.from_string("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            Pubkey.from_string("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            Pubkey.from_string("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            Pubkey.from_string("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
        ], False)
        self.assertEqual(-95744, result1[0].start_tick_index)
        self.assertEqual(-101376, result1[1].start_tick_index)
        self.assertEqual(-107008, result1[2].start_tick_index)
        self.assertEqual(-112640, result1[3].start_tick_index)
        self.assertIsNone(result1[4])
        self.assertIsNone(result1[5])
        self.assertIsNone(result1[6])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(7, len(client.get_multiple_accounts_history))

        result2 = await fetcher.list_tick_arrays([
            Pubkey.from_string("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            Pubkey.from_string("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            Pubkey.from_string("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            Pubkey.from_string("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            Pubkey.from_string("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            Pubkey.from_string("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            Pubkey.from_string("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
        ], False)
        self.assertEqual(-95744, result1[0].start_tick_index)
        self.assertEqual(-101376, result1[1].start_tick_index)
        self.assertEqual(-107008, result1[2].start_tick_index)
        self.assertEqual(-112640, result1[3].start_tick_index)
        self.assertIsNone(result1[4])
        self.assertIsNone(result1[5])
        self.assertIsNone(result1[6])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(2, client.get_multiple_accounts_called)
        self.assertEqual(10, len(client.get_multiple_accounts_history))

    async def test_get_latest_block_timestamp_01(self):
        client = AsyncClientStub([], ASYNC_CLIENT_STUB_BLOCK_SLOT, ASYNC_CLIENT_STUB_BLOCK_TIMESTAMP)
        fetcher = AccountFetcher(client)

        block_timestamp = await fetcher.get_latest_block_timestamp()
        self.assertEqual(ASYNC_CLIENT_STUB_BLOCK_SLOT, block_timestamp.slot)
        self.assertEqual(ASYNC_CLIENT_STUB_BLOCK_TIMESTAMP, block_timestamp.timestamp)

    async def test_get_latest_block_timestamp_02(self):
        client = AsyncClientStub([], ASYNC_CLIENT_STUB_BLOCK_SLOT+1, ASYNC_CLIENT_STUB_BLOCK_TIMESTAMP+1)
        fetcher = AccountFetcher(client)

        block_timestamp = await fetcher.get_latest_block_timestamp()
        self.assertEqual(ASYNC_CLIENT_STUB_BLOCK_SLOT+1, block_timestamp.slot)
        self.assertEqual(ASYNC_CLIENT_STUB_BLOCK_TIMESTAMP+1, block_timestamp.timestamp)


class TokenUtilTestCase(unittest.IsolatedAsyncioTestCase):
    def test_derive_ata_01(self):
        # Token Prograam
        owner = Pubkey.from_string("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6")
        mint = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        result = TokenUtil.derive_ata(owner, mint)
        self.assertEqual(Pubkey.from_string("FbQdXCQgGQYj3xcGeryVVFjKCTsAuu53vmCRtmjQEqM5"), result)

    def test_derive_ata_02(self):
        # Token Prograam
        owner = Pubkey.from_string("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6")
        mint = Pubkey.from_string("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE")
        result = TokenUtil.derive_ata(owner, mint)
        self.assertEqual(Pubkey.from_string("7B8yNHX62NLvRswD86ttbGcV5TYxUsDNxEg2ZRMZLPRt"), result)

    def test_derive_ata_03(self):
        # Token-2022 Prograam
        self.assertTrue(False, "not implemented (Token-2022)")

    async def test_resolve_or_create_ata_01(self):
        client = AsyncClientStub([
            "user_ata_orca.7B8yNHX62NLvRswD86ttbGcV5TYxUsDNxEg2ZRMZLPRt.json"
        ])
        owner = Pubkey.from_string("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6")
        mint = Pubkey.from_string("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE")
        result = await TokenUtil.resolve_or_create_ata(client, owner, mint)
        self.assertEqual(Pubkey.from_string("7B8yNHX62NLvRswD86ttbGcV5TYxUsDNxEg2ZRMZLPRt"), result.pubkey)
        self.assertEqual(0, len(result.instruction.instructions))
        self.assertEqual(0, len(result.instruction.cleanup_instructions))
        self.assertEqual(0, len(result.instruction.signers))

    async def test_resolve_or_create_ata_02(self):
        client = AsyncClientStub([])
        owner = Pubkey.from_string("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6")
        mint = Pubkey.from_string("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE")
        result = await TokenUtil.resolve_or_create_ata(client, owner, mint)
        self.assertEqual(Pubkey.from_string("7B8yNHX62NLvRswD86ttbGcV5TYxUsDNxEg2ZRMZLPRt"), result.pubkey)
        self.assertEqual(1, len(result.instruction.instructions))
        self.assertEqual(0, len(result.instruction.cleanup_instructions))
        self.assertEqual(0, len(result.instruction.signers))

    async def test_resolve_or_create_ata_03(self):
        client = AsyncClientStub([])
        owner = Pubkey.from_string("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6")
        mint = Pubkey.from_string("So11111111111111111111111111111111111111112")
        result = await TokenUtil.resolve_or_create_ata(client, owner, mint, 1000000000)
        self.assertEqual(2, len(result.instruction.instructions))
        self.assertEqual(1, len(result.instruction.cleanup_instructions))
        self.assertEqual(1, len(result.instruction.signers))
        self.assertEqual(result.instruction.signers[0].pubkey(), result.pubkey)

    async def test_resolve_or_create_ata_04(self):
        # Token-2022 Prograam
        self.assertTrue(False, "not implemented (Token-2022)")


if __name__ == "__main__":
    unittest.main()
