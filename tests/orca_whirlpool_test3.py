import unittest
import json
import pathlib
import base64
from typing import Optional, List
from solana.publickey import PublicKey
from solders.account import Account
from solders.pubkey import Pubkey
from solders.rpc.responses import GetAccountInfoResp, GetMultipleAccountsResp, RpcResponseContext, GetLatestBlockhashResp, GetBlockTimeResp
from solana.rpc.async_api import AsyncClient
from solana.rpc import types
from solana.rpc.core import Commitment

from orca_whirlpool.internal.accounts.account_fetcher import AccountFetcher
from orca_whirlpool.internal.utils.token_util import TokenUtil

ACCOUNT_JSON_FILES_DIR = "accounts"
ASYNC_CLIENT_STUB_BLOCK_SLOT = 160156384
ASYNC_CLIENT_STUB_BLOCK_TIMESTAMP = 1668008674
DUMMY_RPC = "http://localhost:8899"


def load_account_json(json_filepath: str) -> (PublicKey, Account):
    with open(json_filepath) as f:
        loaded = json.load(f)
    pubkey = PublicKey(loaded["pubkey"])
    account_json = loaded["account"]

    data_b64 = account_json["data"]
    data = base64.standard_b64decode(data_b64[0])
    lamports = int(account_json["lamports"])
    executable = bool(account_json["executable"])
    owner = Pubkey(bytes(PublicKey(account_json["owner"])))
    rent_epoch = int(account_json["rentEpoch"])

    return pubkey, Account(lamports, data, owner, executable, rent_epoch)


class AsyncClientStub(AsyncClient):
    def __init__(self, account_json_filenames: List[str], block_slot: int = 0, block_timestamp: int = 0):
        super().__init__(DUMMY_RPC)

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
        pubkey: PublicKey,
        commitment: Optional[Commitment] = None,
        encoding: str = "base64",
        data_slice: Optional[types.DataSliceOpts] = None,
    ) -> GetAccountInfoResp:
        self.get_account_info_called += 1
        self.get_account_info_history.append(pubkey)
        return GetAccountInfoResp(self._cache.get(str(pubkey)), RpcResponseContext(0))

    async def get_multiple_accounts(
        self,
        pubkeys: List[PublicKey],
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
        return GetLatestBlockhashResp(None, RpcResponseContext(self.block_slot))

    async def get_block_time(self, slot: int) -> GetBlockTimeResp:
        return GetBlockTimeResp(self.block_timestamp)


class AccountFetcherAndAccountParserTestCase(unittest.TestCase):
    async def test_get_whirlpools_config_01(self):
        client = AsyncClientStub(["whirlpools_config.2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_whirlpools_config(PublicKey("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(PublicKey("3Pi4tc4SxZyKZivKxWnYfGNxeqFJJxPc8xRw1VnvXpbb"), result.fee_authority)
        self.assertEqual(PublicKey("3Pi4tc4SxZyKZivKxWnYfGNxeqFJJxPc8xRw1VnvXpbb"),result.collect_protocol_fees_authority)
        self.assertEqual(PublicKey("DjDsi34mSB66p2nhBL6YvhbcLtZbkGfNybFeLDjJqxJW"), result.reward_emissions_super_authority)
        self.assertEqual(300, result.default_protocol_fee_rate)

    async def test_get_fee_tier_01(self):
        client = AsyncClientStub(["whirlpools_config_feetier64.HT55NVGVTjWmWLjV7BrSMPVZ7ppU8T2xE5nCAZ6YaGad.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_fee_tier(PublicKey("HT55NVGVTjWmWLjV7BrSMPVZ7ppU8T2xE5nCAZ6YaGad"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(PublicKey("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result.whirlpools_config)
        self.assertEqual(64, result.tick_spacing)
        self.assertEqual(3000, result.default_fee_rate)

    async def test_get_whirlpool_01(self):
        client = AsyncClientStub(["sol_usdc_wp_whirlpool.HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_whirlpool(PublicKey("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(PublicKey("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result.whirlpools_config)
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
        self.assertEqual(PublicKey("So11111111111111111111111111111111111111112"), result.token_mint_a)
        self.assertEqual(PublicKey("3YQm7ujtXWJU2e9jhp2QGHpnn1ShXn12QjvzMvDgabpX"), result.token_vault_a)
        self.assertEqual(5195114924723508514, result.fee_growth_global_a)
        self.assertEqual(PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"), result.token_mint_b)
        self.assertEqual(PublicKey("2JTw1fE2wz1SymWUQ7UqpVtrTuKjcd6mWwYwUJUCh2rq"), result.token_vault_b)
        self.assertEqual(219749538362201637, result.fee_growth_global_b)
        self.assertEqual(1659764580, result.reward_last_updated_timestamp)

        self.assertEqual(PublicKey("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE"), result.reward_infos[0].mint)
        self.assertEqual(PublicKey("2tU3tKvj7RBxEatryyMYTUxBoLSSWCQXsdv1X6yce4T2"), result.reward_infos[0].vault)
        self.assertEqual(PublicKey("DjDsi34mSB66p2nhBL6YvhbcLtZbkGfNybFeLDjJqxJW"), result.reward_infos[0].authority)
        self.assertEqual(0, result.reward_infos[0].emissions_per_second_x64)
        self.assertEqual(36063151640940598, result.reward_infos[0].growth_global_x64)

        self.assertEqual(PublicKey("11111111111111111111111111111111"), result.reward_infos[1].mint)
        self.assertEqual(PublicKey("11111111111111111111111111111111"), result.reward_infos[1].vault)
        self.assertEqual(PublicKey("3Pi4tc4SxZyKZivKxWnYfGNxeqFJJxPc8xRw1VnvXpbb"), result.reward_infos[1].authority)
        self.assertEqual(0, result.reward_infos[1].emissions_per_second_x64)
        self.assertEqual(0, result.reward_infos[1].growth_global_x64)

        self.assertEqual(PublicKey("11111111111111111111111111111111"), result.reward_infos[2].mint)
        self.assertEqual(PublicKey("11111111111111111111111111111111"), result.reward_infos[2].vault)
        self.assertEqual(PublicKey("3Pi4tc4SxZyKZivKxWnYfGNxeqFJJxPc8xRw1VnvXpbb"), result.reward_infos[2].authority)
        self.assertEqual(0, result.reward_infos[2].emissions_per_second_x64)
        self.assertEqual(0, result.reward_infos[2].growth_global_x64)

    async def test_get_tick_array_01(self):
        client = AsyncClientStub(["samo_usdc_wp_ta_n112640.CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_tick_array(PublicKey("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(PublicKey("9vqYJjDUFecLL2xPUC4Rc7hyCtZ6iJ4mDiVZX7aFXoAe"), result.whirlpool)
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
        result = await fetcher.get_position(PublicKey("5j3szbi2vnydYoyALNgttPD9YhCNwshUGkhzmzaP4WF7"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(PublicKey("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"), result.whirlpool)
        self.assertEqual(PublicKey("AuB2UXTArEWXCUaNxYPCGKoigjD6cX5BMbXPs8qsEe39"), result.position_mint)
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
        client = AsyncClientStub(["token_orca.orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_token_mint(PublicKey("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(PublicKey("8DzsCSvbvBDYxGB4ytNF698zi6Dyo9dUBVRNjZQFHSUt"), result.mint_authority)
        self.assertEqual(99999990272788, result.supply)
        self.assertEqual(6, result.decimals)
        self.assertEqual(True, result.is_initialized)
        self.assertEqual(PublicKey("11111111111111111111111111111111"), result.freeze_authority)

    async def test_get_token_account_01(self):
        client = AsyncClientStub(["user_ata_orca.7B8yNHX62NLvRswD86ttbGcV5TYxUsDNxEg2ZRMZLPRt.json"])
        fetcher = AccountFetcher(client)
        result = await fetcher.get_token_account(PublicKey("7B8yNHX62NLvRswD86ttbGcV5TYxUsDNxEg2ZRMZLPRt"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        self.assertEqual(PublicKey("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE"), result.mint)
        self.assertEqual(PublicKey("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6"), result.owner)
        self.assertEqual(58875, result.amount)
        self.assertEqual(PublicKey("11111111111111111111111111111111"), result.delegate)
        self.assertEqual(False, result.is_native)
        self.assertEqual(0, result.delegated_amount)
        self.assertEqual(PublicKey("11111111111111111111111111111111"), result.close_authority)

    async def test_list_token_mints_01(self):
        client = AsyncClientStub([
            "token_orca.orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE.json",
            "token_samo.7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU.json",
            "token_usdc.EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v.json",
        ])
        fetcher = AccountFetcher(client)
        result = await fetcher.list_token_mints([
            PublicKey("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE"),
            PublicKey("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"),
            PublicKey("mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So"),
            PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(4, len(client.get_multiple_accounts_history))

        self.assertEqual(PublicKey("8DzsCSvbvBDYxGB4ytNF698zi6Dyo9dUBVRNjZQFHSUt"), result[0].mint_authority)
        self.assertEqual(PublicKey("samohexDip23Xe39eKrndWG25QWSnnckUa2Yc3iEe9v"), result[1].mint_authority)
        self.assertIsNone(result[2])
        self.assertEqual(PublicKey("2wmVCSfPxGPjrnMMn7rchp4uaeoTqN39mXFC2zhPdri9"), result[3].mint_authority)

    async def test_list_token_accounts_01(self):
        client = AsyncClientStub([
            "samo_usdc_wp_vault_a.3xxgYc3jXPdjqpMdrRyKtcddh4ZdtqpaN33fwaWJ2Wbh.json",
            "samo_usdc_wp_vault_b.8xKCx3SGwWR6BUr9mZFm3xwZmCVMuLjXn9iLEU6784FS.json",
            "sol_usdc_wp_vault_a.3YQm7ujtXWJU2e9jhp2QGHpnn1ShXn12QjvzMvDgabpX.json",
            "sol_usdc_wp_vault_b.2JTw1fE2wz1SymWUQ7UqpVtrTuKjcd6mWwYwUJUCh2rq.json",
        ])
        fetcher = AccountFetcher(client)
        result = await fetcher.list_token_accounts([
            PublicKey("3xxgYc3jXPdjqpMdrRyKtcddh4ZdtqpaN33fwaWJ2Wbh"),
            PublicKey("8xKCx3SGwWR6BUr9mZFm3xwZmCVMuLjXn9iLEU6784FS"),
            PublicKey("6dM4iMgSei6zF9y3sqdgSJ2xwNXML5wk5QKhV4DqJPhu"),
            PublicKey("3YQm7ujtXWJU2e9jhp2QGHpnn1ShXn12QjvzMvDgabpX"),
            PublicKey("2JTw1fE2wz1SymWUQ7UqpVtrTuKjcd6mWwYwUJUCh2rq"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(5, len(client.get_multiple_accounts_history))

        self.assertEqual(PublicKey("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"), result[0].mint)
        self.assertEqual(PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"), result[1].mint)
        self.assertIsNone(result[2])
        self.assertEqual(PublicKey("So11111111111111111111111111111111111111112"), result[3].mint)
        self.assertEqual(PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"), result[4].mint)

    async def test_list_whirlpools_01(self):
        client = AsyncClientStub([
            "sol_usdc_wp_whirlpool.HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ.json",
            "samo_usdc_wp_whirlpool.9vqYJjDUFecLL2xPUC4Rc7hyCtZ6iJ4mDiVZX7aFXoAe.json",
        ])
        fetcher = AccountFetcher(client)
        result = await fetcher.list_whirlpools([
            PublicKey("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"),
            PublicKey("9vqYJjDUFecLL2xPUC4Rc7hyCtZ6iJ4mDiVZX7aFXoAe"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(2, len(client.get_multiple_accounts_history))

        self.assertEqual(PublicKey("So11111111111111111111111111111111111111112"), result[0].token_mint_a)
        self.assertEqual(PublicKey("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"), result[1].token_mint_a)

    async def test_list_positions_01(self):
        client = AsyncClientStub([
            "samo_usdc_wp_position.B66pRzGcKMmxRJ16KMkJMJoQWWhmyk4na4DPcv6X5ZRD.json",
            "sol_usdc_wp_position.5j3szbi2vnydYoyALNgttPD9YhCNwshUGkhzmzaP4WF7.json",
        ])
        fetcher = AccountFetcher(client)
        result = await fetcher.list_positions([
            PublicKey("B66pRzGcKMmxRJ16KMkJMJoQWWhmyk4na4DPcv6X5ZRD"),
            PublicKey("5j3szbi2vnydYoyALNgttPD9YhCNwshUGkhzmzaP4WF7"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(2, len(client.get_multiple_accounts_history))

        self.assertEqual(PublicKey("9vqYJjDUFecLL2xPUC4Rc7hyCtZ6iJ4mDiVZX7aFXoAe"), result[0].whirlpool)
        self.assertEqual(PublicKey("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"), result[1].whirlpool)

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
            PublicKey("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            PublicKey("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            PublicKey("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            PublicKey("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            PublicKey("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            PublicKey("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            PublicKey("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
        ])
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(7, len(client.get_multiple_accounts_history))

        self.assertEqual(-95744, result[0].start_tick_index)
        self.assertEqual(-101376, result[1].start_tick_index)
        self.assertEqual(-107008, result[2].start_tick_index)
        self.assertEqual(-112640, result[3].start_tick_index)
        self.assertEqual(-118272, result[4].start_tick_index)
        self.assertEqual(-123904, result[5].start_tick_index)
        self.assertEqual(-129536, result[6].start_tick_index)

    async def test_cache_get_01(self):
        client = AsyncClientStub(["sol_usdc_wp_whirlpool.HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ.json"])
        fetcher = AccountFetcher(client)

        result1 = await fetcher.get_whirlpool(PublicKey("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"))
        self.assertEqual(PublicKey("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result1.whirlpools_config)
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        result2 = await fetcher.get_whirlpool(PublicKey("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"))
        self.assertEqual(PublicKey("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result2.whirlpools_config)
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        result3 = await fetcher.get_whirlpool(PublicKey("2AEWSvUds1wsufnsDPCXjFsJCMJH5SNNm7fSF4kxys9a"))
        self.assertIsNone(result3)
        self.assertEqual(2, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        result4 = await fetcher.get_whirlpool(PublicKey("2AEWSvUds1wsufnsDPCXjFsJCMJH5SNNm7fSF4kxys9a"))
        self.assertIsNone(result4)
        self.assertEqual(3, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        result5 = await fetcher.get_whirlpool(PublicKey("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"))
        self.assertEqual(PublicKey("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result5.whirlpools_config)
        self.assertEqual(3, client.get_account_info_called)
        self.assertEqual(0, client.get_multiple_accounts_called)

        result6 = await fetcher.get_whirlpool(PublicKey("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"), True)
        self.assertEqual(PublicKey("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), result6.whirlpools_config)
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
            PublicKey("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            PublicKey("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            PublicKey("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            # PublicKey("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            # PublicKey("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            # PublicKey("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            # PublicKey("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
        ])
        self.assertEqual(-95744, result1[0].start_tick_index)
        self.assertEqual(-101376, result1[1].start_tick_index)
        self.assertEqual(-107008, result1[2].start_tick_index)
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(3, len(client.get_multiple_accounts_history))

        result2 = await fetcher.list_tick_arrays([
            PublicKey("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            PublicKey("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            PublicKey("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            # PublicKey("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            # PublicKey("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            # PublicKey("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            # PublicKey("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
        ])
        self.assertEqual(-95744, result2[0].start_tick_index)
        self.assertEqual(-101376, result2[1].start_tick_index)
        self.assertEqual(-107008, result2[2].start_tick_index)
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(1, client.get_multiple_accounts_called)
        self.assertEqual(3, len(client.get_multiple_accounts_history))

        result3 = await fetcher.list_tick_arrays([
            PublicKey("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            PublicKey("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            # PublicKey("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            PublicKey("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            PublicKey("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            # PublicKey("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            # PublicKey("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
        ])
        self.assertEqual(-95744, result3[0].start_tick_index)
        self.assertEqual(-101376, result3[1].start_tick_index)
        self.assertEqual(-112640, result3[2].start_tick_index)
        self.assertEqual(-118272, result3[3].start_tick_index)
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(2, client.get_multiple_accounts_called)
        self.assertEqual(5, len(client.get_multiple_accounts_history))

        result4 = await fetcher.list_tick_arrays([
            PublicKey("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            PublicKey("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            # PublicKey("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            PublicKey("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            PublicKey("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            # PublicKey("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            # PublicKey("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
        ], True)
        self.assertEqual(-95744, result4[0].start_tick_index)
        self.assertEqual(-101376, result4[1].start_tick_index)
        self.assertEqual(-112640, result4[2].start_tick_index)
        self.assertEqual(-118272, result4[3].start_tick_index)
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(3, client.get_multiple_accounts_called)
        self.assertEqual(9, len(client.get_multiple_accounts_history))

        result5 = await fetcher.get_tick_array(PublicKey("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"))
        self.assertEqual(0, client.get_account_info_called)
        self.assertEqual(3, client.get_multiple_accounts_called)
        self.assertEqual(9, len(client.get_multiple_accounts_history))

        result6 = await fetcher.get_tick_array(PublicKey("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"))
        self.assertEqual(1, client.get_account_info_called)
        self.assertEqual(3, client.get_multiple_accounts_called)
        self.assertEqual(9, len(client.get_multiple_accounts_history))

        result7 = await fetcher.get_tick_array(PublicKey("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"))
        self.assertEqual(2, client.get_account_info_called)
        self.assertEqual(3, client.get_multiple_accounts_called)
        self.assertEqual(9, len(client.get_multiple_accounts_history))

        result8 = await fetcher.get_tick_array(PublicKey("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"))
        self.assertEqual(3, client.get_account_info_called)
        self.assertEqual(3, client.get_multiple_accounts_called)
        self.assertEqual(9, len(client.get_multiple_accounts_history))

        result9 = await fetcher.list_tick_arrays([
            PublicKey("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            PublicKey("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            PublicKey("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            PublicKey("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            PublicKey("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            PublicKey("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            PublicKey("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
        ], False)
        self.assertEqual(3, client.get_account_info_called)
        self.assertEqual(3, client.get_multiple_accounts_called)
        self.assertEqual(9, len(client.get_multiple_accounts_history))

        result10 = await fetcher.get_tick_array(PublicKey("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"))
        self.assertEqual(4, client.get_account_info_called)
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
            PublicKey("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            PublicKey("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            PublicKey("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            PublicKey("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            PublicKey("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            PublicKey("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            PublicKey("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
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
            PublicKey("C9ahCpEXEysPgA3NGZVqZcVViBoXpoS68tbo2pC4FNHH"),
            PublicKey("HpuNjdx9vTLYTAsxH3N6HCkguEkG9mCEpkrRugqyCPwF"),
            PublicKey("EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ"),
            PublicKey("CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH"),
            PublicKey("4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G"),
            PublicKey("Gad6jpBXSxFmSqcPSPTE9jABp9ragNc2VsdUCNWLEAMT"),
            PublicKey("ArnRmfQ49b2otrns9Kjug8fZXS8UdmKtxR2arpaevtxq"),
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


class TokeUtilTestCase(unittest.TestCase):
    def test_derive_ata_01(self):
        owner = PublicKey("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6")
        mint = PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        result = TokenUtil.derive_ata(owner, mint)
        self.assertEqual(PublicKey("FbQdXCQgGQYj3xcGeryVVFjKCTsAuu53vmCRtmjQEqM5"), result)

    def test_derive_ata_02(self):
        owner = PublicKey("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6")
        mint = PublicKey("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE")
        result = TokenUtil.derive_ata(owner, mint)
        self.assertEqual(PublicKey("7B8yNHX62NLvRswD86ttbGcV5TYxUsDNxEg2ZRMZLPRt"), result)

    async def test_resolve_or_create_ata_01(self):
        client = AsyncClientStub([
            "user_ata_orca.7B8yNHX62NLvRswD86ttbGcV5TYxUsDNxEg2ZRMZLPRt.json"
        ])
        owner = PublicKey("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6")
        mint = PublicKey("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE")
        result = await TokenUtil.resolve_or_create_ata(client, owner, mint)
        self.assertEqual(PublicKey("7B8yNHX62NLvRswD86ttbGcV5TYxUsDNxEg2ZRMZLPRt"), result.pubkey)
        self.assertEqual(0, len(result.instruction.instructions))
        self.assertEqual(0, len(result.instruction.cleanup_instructions))
        self.assertEqual(0, len(result.instruction.signers))

    async def test_resolve_or_create_ata_02(self):
        client = AsyncClientStub([])
        owner = PublicKey("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6")
        mint = PublicKey("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE")
        result = await TokenUtil.resolve_or_create_ata(client, owner, mint)
        self.assertEqual(PublicKey("7B8yNHX62NLvRswD86ttbGcV5TYxUsDNxEg2ZRMZLPRt"), result.pubkey)
        self.assertEqual(1, len(result.instruction.instructions))
        self.assertEqual(0, len(result.instruction.cleanup_instructions))
        self.assertEqual(0, len(result.instruction.signers))

    async def test_resolve_or_create_ata_03(self):
        client = AsyncClientStub([])
        owner = PublicKey("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6")
        mint = PublicKey("So11111111111111111111111111111111111111112")
        result = await TokenUtil.resolve_or_create_ata(client, owner, mint, 1000000000)
        self.assertEqual(2, len(result.instruction.instructions))
        self.assertEqual(1, len(result.instruction.cleanup_instructions))
        self.assertEqual(1, len(result.instruction.signers))
        self.assertEqual(result.instruction.signers[0].public_key, result.pubkey)


if __name__ == "__main__":
    unittest.main()
