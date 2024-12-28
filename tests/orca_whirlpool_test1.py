import unittest
from decimal import Decimal
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey

from orca_whirlpool.internal.constants import ORCA_WHIRLPOOL_PROGRAM_ID, ORCA_WHIRLPOOLS_CONFIG, ORCA_WHIRLPOOLS_CONFIG_EXTENSION, MIN_TICK_INDEX, MAX_TICK_INDEX, MIN_SQRT_PRICE, MAX_SQRT_PRICE, U64_MAX, TICK_ARRAY_SIZE, FEE_RATE_MUL_VALUE, PROTOCOL_FEE_RATE_MUL_VALUE, NUM_REWARDS, MAX_SWAP_TICK_ARRAYS, METAPLEX_METADATA_PROGRAM_ID, ORCA_WHIRLPOOL_NFT_UPDATE_AUTHORITY, DEFAULT_PUBKEY
from orca_whirlpool.internal.utils.pool_util import PoolUtil
from orca_whirlpool.internal.utils.position_util import PositionUtil
from orca_whirlpool.internal.utils.price_math import PriceMath
from orca_whirlpool.internal.utils.swap_util import SwapUtil
from orca_whirlpool.internal.utils.pda_util import PDAUtil
from orca_whirlpool.internal.utils.tick_util import TickUtil
from orca_whirlpool.internal.utils.liquidity_math import LiquidityMath
from orca_whirlpool.internal.context import WhirlpoolContext
from orca_whirlpool.internal.accounts.account_fetcher import AccountFetcher
from orca_whirlpool.internal.types.types import TokenAmounts
from orca_whirlpool.internal.types.enums import PositionStatus, SpecifiedAmount, SwapDirection
from orca_whirlpool.internal.anchor.types import WhirlpoolRewardInfo


class ConstantsTestCase(unittest.TestCase):
    def test_ORCA_WHIRLPOOL_PROGRAM_ID(self):
        self.assertEqual(Pubkey.from_string("whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc"), ORCA_WHIRLPOOL_PROGRAM_ID)

    def test_ORCA_WHIRLPOOLS_CONFIG(self):
        self.assertEqual(Pubkey.from_string("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ"), ORCA_WHIRLPOOLS_CONFIG.SOLANA_MAINNET)
        self.assertEqual(Pubkey.from_string("FcrweFY1G9HJAHG5inkGB6pKg1HZ6x9UC2WioAfWrGkR"), ORCA_WHIRLPOOLS_CONFIG.SOLANA_DEVNET)
        self.assertEqual(Pubkey.from_string("FVG4oDbGv16hqTUbovjyGmtYikn6UBEnazz6RVDMEFwv"), ORCA_WHIRLPOOLS_CONFIG.ECLIPSE_MAINNET)
        self.assertEqual(Pubkey.from_string("FPydDjRdZu9sT7HVd6ANhfjh85KLq21Pefr5YWWMRPFp"), ORCA_WHIRLPOOLS_CONFIG.ECLIPSE_TESTNET)

    def test_ORCA_WHIRLPOOLS_CONFIG_EXTENSION(self):
        self.assertEqual(Pubkey.from_string("777H5H3Tp9U11uRVRzFwM8BinfiakbaLT8vQpeuhvEiH"), ORCA_WHIRLPOOLS_CONFIG_EXTENSION.SOLANA_MAINNET)
        self.assertEqual(Pubkey.from_string("475EJ7JqnRpVLoFVzp2ruEYvWWMCf6Z8KMWRujtXXNSU"), ORCA_WHIRLPOOLS_CONFIG_EXTENSION.SOLANA_DEVNET)
        self.assertEqual(Pubkey.from_string("9VrJciULifYcwu2CL8nbXdw4deqQgmv7VTzidwgQYBmm"), ORCA_WHIRLPOOLS_CONFIG_EXTENSION.ECLIPSE_MAINNET)
        self.assertEqual(Pubkey.from_string("6gUEB962oFdZtwoVyXNya9TfGWnBEbYNYt8UdvzT6PSf"), ORCA_WHIRLPOOLS_CONFIG_EXTENSION.ECLIPSE_TESTNET)

    def test_ORCA_WHIRLPOOL_NFT_UPDATE_AUTHORITY(self):
        self.assertEqual(Pubkey.from_string("3axbTs2z5GBy6usVbNVoqEgZMng3vZvMnAoX29BFfwhr"), ORCA_WHIRLPOOL_NFT_UPDATE_AUTHORITY)

    def test_DEFAULT_PUBKEY(self):
        self.assertEqual(Pubkey.from_string("11111111111111111111111111111111"), DEFAULT_PUBKEY)

    def test_NUM_REWARDS(self):
        self.assertEqual(3, NUM_REWARDS)

    def test_MAX_TICK_INDEX(self):
        self.assertEqual(443636, MAX_TICK_INDEX)

    def test_MIN_TICK_INDEX(self):
        self.assertEqual(-443636, MIN_TICK_INDEX)

    def test_MAX_SQRT_PRICE(self):
        self.assertEqual(79226673515401279992447579055, MAX_SQRT_PRICE)

    def test_MIN_SQRT_PRICE(self):
        self.assertEqual(4295048016, MIN_SQRT_PRICE)

    def test_TICK_ARRAY_SIZE(self):
        self.assertEqual(88, TICK_ARRAY_SIZE)

    def test_METADATA_PROGRAM_ADDRESS(self):
        self.assertEqual(Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"), METAPLEX_METADATA_PROGRAM_ID)

    def test_MAX_SWAP_TICK_ARRAYS(self):
        self.assertEqual(3, MAX_SWAP_TICK_ARRAYS)

    def test_PROTOCOL_FEE_RATE_MUL_VALUE(self):
        self.assertEqual(10000, PROTOCOL_FEE_RATE_MUL_VALUE)

    def test_FEE_RATE_MUL_VALUE(self):
        self.assertEqual(1000000, FEE_RATE_MUL_VALUE)

    def test_U64_MAX(self):
        self.assertEqual(2**64-1, U64_MAX)


class PDAUtilTestCase(unittest.TestCase):
    def test_get_whirlpool_01(self):
        sol = Pubkey.from_string("So11111111111111111111111111111111111111112")
        usdc = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        sol_usdc_64 = Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ")
        result = PDAUtil.get_whirlpool(ORCA_WHIRLPOOL_PROGRAM_ID, ORCA_WHIRLPOOLS_CONFIG.SOLANA_MAINNET, sol, usdc, 64).pubkey
        self.assertEqual(str(sol_usdc_64), str(result))

    def test_get_whirlpool_02(self):
        sol = Pubkey.from_string("So11111111111111111111111111111111111111112")
        stsol = Pubkey.from_string("7dHbWXmci3dT8UFYWYZweBLXgycu7Y3iL6trKn1Y7ARj")
        sol_stsol_1 = Pubkey.from_string("2AEWSvUds1wsufnsDPCXjFsJCMJH5SNNm7fSF4kxys9a")
        result = PDAUtil.get_whirlpool(ORCA_WHIRLPOOL_PROGRAM_ID, ORCA_WHIRLPOOLS_CONFIG.SOLANA_MAINNET, sol, stsol, 1).pubkey
        self.assertEqual(str(sol_stsol_1), str(result))

    def test_get_position_01(self):
        # https://solscan.io/tx/32boMycNhPh8JSAtiBT53pWgKprmpHMWyGaCdAjqNvg2ppB9GV3M7Ye2MVhmGLbEBqFxN1acNjMRvSvcriYNcD2v
        mint = Pubkey.from_string("BsNH5iSWjthsDuJrh5QeVGUjbkUcxkjaGzByjVjt83qC")
        position = Pubkey.from_string("88hXrRdXuHFCWm41S6yyeW7QWSeVbgmHL4ja2iHUumip")
        result = PDAUtil.get_position(ORCA_WHIRLPOOL_PROGRAM_ID, mint).pubkey
        self.assertEqual(str(position), str(result))

    def test_get_position_02(self):
        # https://solscan.io/tx/4L2jje9mTXygt9x7oyf7sCoiuSgG5axpMBFNVT1Hg6tESW4rJnrPACzBE1gcz82J1ckrN2PubhvN2tEsJmbcDyL7
        mint = Pubkey.from_string("Fcjdf8RQBRwZqDUJ4Kqe7K4T3jG1rtchKywWN1BKD1k7")
        position = Pubkey.from_string("B66pRzGcKMmxRJ16KMkJMJoQWWhmyk4na4DPcv6X5ZRD")
        result = PDAUtil.get_position(ORCA_WHIRLPOOL_PROGRAM_ID, mint).pubkey
        self.assertEqual(str(position), str(result))

    def test_get_position_metadata_01(self):
        # https://solscan.io/tx/32boMycNhPh8JSAtiBT53pWgKprmpHMWyGaCdAjqNvg2ppB9GV3M7Ye2MVhmGLbEBqFxN1acNjMRvSvcriYNcD2v
        mint = Pubkey.from_string("BsNH5iSWjthsDuJrh5QeVGUjbkUcxkjaGzByjVjt83qC")
        metadata = Pubkey.from_string("38SUhTtHdSDCyb69pLJ5ranDoyKPkdNB47fNiGDMCZgc")
        result = PDAUtil.get_position_metadata(mint).pubkey
        self.assertEqual(str(metadata), str(result))

    def test_get_position_metadata_02(self):
        # https://solscan.io/tx/4L2jje9mTXygt9x7oyf7sCoiuSgG5axpMBFNVT1Hg6tESW4rJnrPACzBE1gcz82J1ckrN2PubhvN2tEsJmbcDyL7
        mint = Pubkey.from_string("Fcjdf8RQBRwZqDUJ4Kqe7K4T3jG1rtchKywWN1BKD1k7")
        metadata = Pubkey.from_string("BynyGEfNoPGJTkKz7ctEeB6CMr6xbYD8QJgU4k7KqBpK")
        result = PDAUtil.get_position_metadata(mint).pubkey
        self.assertEqual(str(metadata), str(result))

    def test_get_tick_array_01(self):
        sol_usdc_64 = Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ")
        tickarray_n39424 = Pubkey.from_string("EVqGhR2ukNuqZNfvFFAitrX6UqrRm2r8ayKX9LH9xHzK")
        result = PDAUtil.get_tick_array(ORCA_WHIRLPOOL_PROGRAM_ID, sol_usdc_64, -39424).pubkey
        self.assertEqual(str(tickarray_n39424), str(result))

    def test_get_tick_array_02(self):
        usdc_usdt_1 = Pubkey.from_string("4fuUiYxTQ6QCrdSq9ouBYcTM7bqSwYTSyLueGZLTy4T4")
        tickarray_p1144 = Pubkey.from_string("9GyHXzDr7XXYYgP4hSf1UXSdCk78kjFQGgZ4zga8VLAg")
        result = PDAUtil.get_tick_array(ORCA_WHIRLPOOL_PROGRAM_ID, usdc_usdt_1, +1144).pubkey
        self.assertEqual(str(tickarray_p1144), str(result))

    def test_get_oracle_01(self):
        sol_usdc_64 = Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ")
        oracle = Pubkey.from_string("4GkRbcYg1VKsZropgai4dMf2Nj2PkXNLf43knFpavrSi")
        result = PDAUtil.get_oracle(ORCA_WHIRLPOOL_PROGRAM_ID, sol_usdc_64).pubkey
        self.assertEqual(str(oracle), str(result))

    def test_get_oracle_02(self):
        usdc_usdt_1 = Pubkey.from_string("4fuUiYxTQ6QCrdSq9ouBYcTM7bqSwYTSyLueGZLTy4T4")
        oracle = Pubkey.from_string("3NxDBWt55DZnEwwQ2bhQ3xWG8Jd18TdUXAG4Zdr7jDai")
        result = PDAUtil.get_oracle(ORCA_WHIRLPOOL_PROGRAM_ID, usdc_usdt_1).pubkey
        self.assertEqual(str(oracle), str(result))

    def test_get_fee_tier_01(self):
        fee_tier_1 = Pubkey.from_string("62dSkn5ktwY1PoKPNMArZA4bZsvyemuknWUnnQ2ATTuN")
        result = PDAUtil.get_fee_tier(ORCA_WHIRLPOOL_PROGRAM_ID, ORCA_WHIRLPOOLS_CONFIG.SOLANA_MAINNET, 1).pubkey
        self.assertEqual(str(fee_tier_1), str(result))

    def test_get_fee_tier_02(self):
        fee_tier_64 = Pubkey.from_string("HT55NVGVTjWmWLjV7BrSMPVZ7ppU8T2xE5nCAZ6YaGad")
        result = PDAUtil.get_fee_tier(ORCA_WHIRLPOOL_PROGRAM_ID, ORCA_WHIRLPOOLS_CONFIG.SOLANA_MAINNET, 64).pubkey
        self.assertEqual(str(fee_tier_64), str(result))

    def test_get_whirlpools_config_extension_01(self):
        config_extension = Pubkey.from_string("777H5H3Tp9U11uRVRzFwM8BinfiakbaLT8vQpeuhvEiH")
        result = PDAUtil.get_whirlpools_config_extension(ORCA_WHIRLPOOL_PROGRAM_ID, ORCA_WHIRLPOOLS_CONFIG.SOLANA_MAINNET).pubkey
        self.assertEqual(str(config_extension), str(result))

    def test_get_token_badge_01(self):
        pyusd = Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo")
        pyusd_token_badge = Pubkey.from_string("HX5iftnCxhtu11ys3ZuWbvUqo7cyPYaVNZBrLL67Hrbm")
        result = PDAUtil.get_token_badge(ORCA_WHIRLPOOL_PROGRAM_ID, ORCA_WHIRLPOOLS_CONFIG.SOLANA_MAINNET, pyusd).pubkey
        self.assertEqual(str(pyusd_token_badge), str(result))


class PriceMathTestCase(unittest.TestCase):
    def test_tick_index_to_sqrt_price_x64_01(self):
        result = PriceMath.tick_index_to_sqrt_price_x64(0)
        expected = 1 << 64
        self.assertEqual(expected, result)

    def test_tick_index_to_sqrt_price_x64_02(self):
        result = PriceMath.tick_index_to_sqrt_price_x64(MIN_TICK_INDEX)
        expected = MIN_SQRT_PRICE
        self.assertEqual(expected, result)

    def test_tick_index_to_sqrt_price_x64_03(self):
        result = PriceMath.tick_index_to_sqrt_price_x64(MAX_TICK_INDEX)
        expected = MAX_SQRT_PRICE
        self.assertEqual(expected, result)

    def test_tick_index_to_sqrt_price_x64_04(self):
        result = PriceMath.tick_index_to_sqrt_price_x64(-39424)
        expected = 2569692997056777477
        self.assertEqual(expected, result)

    def test_tick_index_to_sqrt_price_x64_05(self):
        result = PriceMath.tick_index_to_sqrt_price_x64(1584)
        expected = 19967060128772183316
        self.assertEqual(expected, result)

    def test_sqrt_price_x64_to_tick_index_01(self):
        result = PriceMath.sqrt_price_x64_to_tick_index(1 << 64)
        expected = 0
        self.assertEqual(expected, result)

    def test_sqrt_price_x64_to_tick_index_02(self):
        result = PriceMath.sqrt_price_x64_to_tick_index(MIN_SQRT_PRICE)
        expected = MIN_TICK_INDEX
        self.assertEqual(expected, result)

    def test_sqrt_price_x64_to_tick_index_03(self):
        result = PriceMath.sqrt_price_x64_to_tick_index(MAX_SQRT_PRICE)
        expected = MAX_TICK_INDEX
        self.assertEqual(expected, result)

    def test_sqrt_price_x64_to_tick_index_04(self):
        result = PriceMath.sqrt_price_x64_to_tick_index(2569692997056777477)
        expected = -39424
        self.assertEqual(expected, result)

    def test_sqrt_price_x64_to_tick_index_05(self):
        result = PriceMath.sqrt_price_x64_to_tick_index(19967060128772183316)
        expected = 1584
        self.assertEqual(expected, result)

    def test_sqrt_price_x64_to_price_01(self):
        result = PriceMath.sqrt_price_x64_to_price(1 << 64, 9, 6)
        expected = 1000
        self.assertEqual(expected, result)

    def test_sqrt_price_x64_to_price_02(self):
        result = PriceMath.sqrt_price_x64_to_price(3262859719519939898, 9, 6)
        expected = Decimal("31.28652726145901582501523855769873785412")
        self.assertTrue(abs(result - expected) < 0.000000001)

    def test_sqrt_price_x64_to_price_03(self):
        result = PriceMath.sqrt_price_x64_to_price(17883737353544829048, 9, 9)
        expected = Decimal("0.9398901994968307280837320329027312154207")
        self.assertTrue(abs(result - expected) < 0.000000001)

    def test_tick_index_to_price_01(self):
        result = PriceMath.tick_index_to_price(0, 9, 6)
        expected = Decimal("1000")
        self.assertTrue(abs(result - expected) < 0.000000001)

    def test_tick_index_to_price_02(self):
        result = PriceMath.tick_index_to_price(-34648, 9, 6)
        expected = Decimal("31.28467958014976245254594473693319568663")
        self.assertTrue(abs(result - expected) < 0.000000001)

    def test_price_to_sqrt_price_x64_01(self):
        expected = 3262859719519939898
        price = PriceMath.sqrt_price_x64_to_price(expected, 9, 6)
        result = PriceMath.price_to_sqrt_price_x64(price, 9, 6)
        self.assertEqual(expected, result)

    def test_price_to_sqrt_price_x64_02(self):
        expected = 17883737353544829048
        price = PriceMath.sqrt_price_x64_to_price(expected, 9, 9)
        result = PriceMath.price_to_sqrt_price_x64(price, 9, 9)
        self.assertEqual(expected, result)

    def test_price_to_tick_index_01(self):
        price = Decimal("31.28652726145901582501523855769873785412")
        result = PriceMath.price_to_tick_index(price, 9, 6)
        expected = -34648
        self.assertEqual(expected, result)

    def test_price_to_tick_index_02(self):
        price = Decimal("0.9398901994968307280837320329027312154207")
        result = PriceMath.price_to_tick_index(price, 9, 9)
        expected = -620
        self.assertEqual(expected, result)

    def test_price_to_tick_index_03(self):
        price = Decimal("1000")
        result = PriceMath.price_to_tick_index(price, 9, 6)
        expected = 0
        self.assertEqual(expected, result)

    def test_price_to_initializable_tick_index_01(self):
        price = Decimal("31.28652726145901582501523855769873785412")
        result = PriceMath.price_to_initializable_tick_index(price, 9, 6, 64)
        expected = -34624
        self.assertEqual(expected, result)

    def test_price_to_initializable_tick_index_02(self):
        price = Decimal("0.9398901994968307280837320329027312154207")
        result = PriceMath.price_to_initializable_tick_index(price, 9, 9, 1)
        expected = -620
        self.assertEqual(expected, result)


class TickUtilTestCase(unittest.TestCase):
    def test_get_initializable_tick_index_01(self):
        result = TickUtil.get_initializable_tick_index(63, 1)
        expected = 63
        self.assertEqual(expected, result)

    def test_get_initializable_tick_index_02(self):
        result = TickUtil.get_initializable_tick_index(-63, 1)
        expected = -63
        self.assertEqual(expected, result)

    def test_get_initializable_tick_index_03(self):
        result = TickUtil.get_initializable_tick_index(63, 64)
        expected = 0
        self.assertEqual(expected, result)

    def test_get_initializable_tick_index_04(self):
        result = TickUtil.get_initializable_tick_index(-63, 64)
        expected = 0
        self.assertEqual(expected, result)

    def test_get_initializable_tick_index_05(self):
        result = TickUtil.get_initializable_tick_index(65, 64)
        expected = 64
        self.assertEqual(expected, result)

    def test_get_initializable_tick_index_06(self):
        result = TickUtil.get_initializable_tick_index(-65, 64)
        expected = -64
        self.assertEqual(expected, result)

    def test_get_start_tick_index_01(self):
        tick_spacing = 1
        result = TickUtil.get_start_tick_index(0, tick_spacing)
        expected = 0
        self.assertEqual(expected, result)

    def test_get_start_tick_index_02(self):
        tick_spacing = 1
        result = TickUtil.get_start_tick_index(tick_spacing*TICK_ARRAY_SIZE - 1, tick_spacing)
        expected = 0
        self.assertEqual(expected, result)

    def test_get_start_tick_index_03(self):
        tick_spacing = 1
        result = TickUtil.get_start_tick_index(tick_spacing*TICK_ARRAY_SIZE, tick_spacing)
        expected = tick_spacing*TICK_ARRAY_SIZE
        self.assertEqual(expected, result)

    def test_get_start_tick_index_04(self):
        tick_spacing = 1
        result = TickUtil.get_start_tick_index(-1, tick_spacing)
        expected = -1 * tick_spacing*TICK_ARRAY_SIZE
        self.assertEqual(expected, result)

    def test_get_start_tick_index_05(self):
        tick_spacing = 1
        result = TickUtil.get_start_tick_index(-1 * tick_spacing*TICK_ARRAY_SIZE, tick_spacing)
        expected = -1 * tick_spacing*TICK_ARRAY_SIZE
        self.assertEqual(expected, result)

    def test_get_start_tick_index_06(self):
        tick_spacing = 64
        result = TickUtil.get_start_tick_index(tick_spacing*TICK_ARRAY_SIZE+64, tick_spacing)
        expected = tick_spacing*TICK_ARRAY_SIZE
        self.assertEqual(expected, result)

    def test_get_start_tick_index_07(self):
        tick_spacing = 64
        result = TickUtil.get_start_tick_index(-1, tick_spacing)
        expected = -1 * tick_spacing*TICK_ARRAY_SIZE
        self.assertEqual(expected, result)

    def test_get_start_tick_index_08(self):
        tick_spacing = 64
        result = TickUtil.get_start_tick_index(tick_spacing, tick_spacing, 2)
        expected = 2 * tick_spacing*TICK_ARRAY_SIZE
        self.assertEqual(expected, result)

    def test_get_start_tick_index_09(self):
        tick_spacing = 64
        result = TickUtil.get_start_tick_index(tick_spacing, tick_spacing, -2)
        expected = -2 * tick_spacing*TICK_ARRAY_SIZE
        self.assertEqual(expected, result)

    def test_get_start_tick_index_10(self):
        tick_spacing = 64
        result = TickUtil.get_start_tick_index(MAX_TICK_INDEX, tick_spacing)
        expected = 439296
        self.assertEqual(expected, result)

    def test_get_start_tick_index_11(self):
        tick_spacing = 64
        result = TickUtil.get_start_tick_index(MIN_TICK_INDEX, tick_spacing)
        expected = -444928
        self.assertEqual(expected, result)

    def test_is_initializable_tick_index_01(self):
        tick_spacing = 1
        result = TickUtil.is_initializable_tick_index(63, tick_spacing)
        expected = True
        self.assertEqual(expected, result)

    def test_is_initializable_tick_index_02(self):
        tick_spacing = 1
        result = TickUtil.is_initializable_tick_index(-63, tick_spacing)
        expected = True
        self.assertEqual(expected, result)

    def test_is_initializable_tick_index_03(self):
        tick_spacing = 64
        result = TickUtil.is_initializable_tick_index(63, tick_spacing)
        expected = False
        self.assertEqual(expected, result)

    def test_is_initializable_tick_index_04(self):
        tick_spacing = 64
        result = TickUtil.is_initializable_tick_index(-63, tick_spacing)
        expected = False
        self.assertEqual(expected, result)

    def test_is_initializable_tick_index_05(self):
        tick_spacing = 64
        result = TickUtil.is_initializable_tick_index(128, tick_spacing)
        expected = True
        self.assertEqual(expected, result)

    def test_is_initializable_tick_index_06(self):
        tick_spacing = 64
        result = TickUtil.is_initializable_tick_index(-1024, tick_spacing)
        expected = True
        self.assertEqual(expected, result)

    def test_is_tick_index_in_bounds_01(self):
        self.assertTrue(TickUtil.is_tick_index_in_bounds(0))

    def test_is_tick_index_in_bounds_02(self):
        self.assertTrue(TickUtil.is_tick_index_in_bounds(64))

    def test_is_tick_index_in_bounds_03(self):
        self.assertTrue(TickUtil.is_tick_index_in_bounds(MIN_TICK_INDEX))

    def test_is_tick_index_in_bounds_04(self):
        self.assertTrue(TickUtil.is_tick_index_in_bounds(MAX_TICK_INDEX))

    def test_is_tick_index_in_bounds_05(self):
        self.assertFalse(TickUtil.is_tick_index_in_bounds(MIN_TICK_INDEX-1))

    def test_is_tick_index_in_bounds_06(self):
        self.assertFalse(TickUtil.is_tick_index_in_bounds(MAX_TICK_INDEX+1))


class SwapUtilTestCase(unittest.TestCase):
    def test_get_default_sqrt_price_limit_01(self):
        result = SwapUtil.get_default_sqrt_price_limit(SwapDirection.AtoB)
        expected = MIN_SQRT_PRICE
        self.assertEqual(expected, result)

    def test_get_default_sqrt_price_limit_02(self):
        result = SwapUtil.get_default_sqrt_price_limit(SwapDirection.BtoA)
        expected = MAX_SQRT_PRICE
        self.assertEqual(expected, result)

    def test_get_default_other_amount_threshold_01(self):
        result = SwapUtil.get_default_other_amount_threshold(SpecifiedAmount.SwapInput)
        expected = 0
        self.assertEqual(expected, result)

    def test_get_default_other_amount_threshold_02(self):
        result = SwapUtil.get_default_other_amount_threshold(SpecifiedAmount.SwapOutput)
        expected = U64_MAX
        self.assertEqual(expected, result)


class LiquidityMathTestCase(unittest.TestCase):
    def test_get_token_amounts_from_liquidity_01(self):
        # in case
        result = LiquidityMath.get_token_amounts_from_liquidity(
            6638825,
            3263190564384012888,
            PriceMath.tick_index_to_sqrt_price_x64(-36864),
            PriceMath.tick_index_to_sqrt_price_x64(-22976),
            True
        )
        self.assertEqual(16588789, result.token_a)
        self.assertEqual(123305, result.token_b)

    def test_get_token_amounts_from_liquidity_02(self):
        # in case
        result = LiquidityMath.get_token_amounts_from_liquidity(
            6638825,
            3263190564384012888,
            PriceMath.tick_index_to_sqrt_price_x64(-36864),
            PriceMath.tick_index_to_sqrt_price_x64(-22976),
            False
        )
        self.assertEqual(16588789 - 1, result.token_a)
        self.assertEqual(123305 - 1, result.token_b)

    def test_get_token_amounts_from_liquidity_03(self):
        # out case (above)
        result = LiquidityMath.get_token_amounts_from_liquidity(
            3402372134,
            18437930740620451432,
            PriceMath.tick_index_to_sqrt_price_x64(-21),
            PriceMath.tick_index_to_sqrt_price_x64(-19),
            True
        )
        self.assertEqual(0, result.token_a)
        self.assertEqual(339881, result.token_b)

    def test_get_token_amounts_from_liquidity_04(self):
        # out case (below)
        result = LiquidityMath.get_token_amounts_from_liquidity(
            41191049234,
            17883939350511009793,
            PriceMath.tick_index_to_sqrt_price_x64(-592),
            PriceMath.tick_index_to_sqrt_price_x64(-589),
            True
        )
        self.assertEqual(6363475, result.token_a)
        self.assertEqual(0, result.token_b)

    def test_get_max_liquidity_from_token_amounts_01(self):
        # in case
        result = LiquidityMath.get_max_liquidity_from_token_amounts(
            3263190564384012888,
            PriceMath.tick_index_to_sqrt_price_x64(-36864),
            PriceMath.tick_index_to_sqrt_price_x64(-22976),
            TokenAmounts(16588789, 123305)
        )
        expected = 6638825
        self.assertEqual(expected, result)

    def test_get_max_liquidity_from_token_amounts_02(self):
        # in case
        result = LiquidityMath.get_max_liquidity_from_token_amounts(
            3263190564384012888,
            PriceMath.tick_index_to_sqrt_price_x64(-36864),
            PriceMath.tick_index_to_sqrt_price_x64(-22976),
            TokenAmounts(16588789, 123305*2)
        )
        expected = 6638825
        self.assertEqual(expected, result)

    def test_get_max_liquidity_from_token_amounts_03(self):
        # in case
        result = LiquidityMath.get_max_liquidity_from_token_amounts(
            3263190564384012888,
            PriceMath.tick_index_to_sqrt_price_x64(-36864),
            PriceMath.tick_index_to_sqrt_price_x64(-22976),
            TokenAmounts(16588789*2, 123305)
        )
        expected = 6638830
        self.assertEqual(expected, result)

    def test_get_max_liquidity_from_token_amounts_04(self):
        # out case (above)
        result = LiquidityMath.get_max_liquidity_from_token_amounts(
            18437930740620451432,
            PriceMath.tick_index_to_sqrt_price_x64(-21),
            PriceMath.tick_index_to_sqrt_price_x64(-19),
            TokenAmounts(0, 339881)
        )
        expected = 3402380446
        self.assertEqual(expected, result)

    def test_get_max_liquidity_from_token_amounts_05(self):
        # out case (above)
        result = LiquidityMath.get_max_liquidity_from_token_amounts(
            18437930740620451432,
            PriceMath.tick_index_to_sqrt_price_x64(-21),
            PriceMath.tick_index_to_sqrt_price_x64(-19),
            TokenAmounts(U64_MAX, 339881)
        )
        expected = 3402380446
        self.assertEqual(expected, result)

    def test_get_max_liquidity_from_token_amounts_06(self):
        # out case (below)
        result = LiquidityMath.get_max_liquidity_from_token_amounts(
            17883939350511009793,
            PriceMath.tick_index_to_sqrt_price_x64(-592),
            PriceMath.tick_index_to_sqrt_price_x64(-589),
            TokenAmounts(6363475, 0)
        )
        expected = 41191052885
        self.assertEqual(expected, result)

    def test_get_max_liquidity_from_token_amounts_07(self):
        # out case (below)
        result = LiquidityMath.get_max_liquidity_from_token_amounts(
            17883939350511009793,
            PriceMath.tick_index_to_sqrt_price_x64(-592),
            PriceMath.tick_index_to_sqrt_price_x64(-589),
            TokenAmounts(6363475, U64_MAX)
        )
        expected = 41191052885
        self.assertEqual(expected, result)

    def test_get_token_a_from_liquidity_01(self):
        result = LiquidityMath.get_token_a_from_liquidity(
            6638825,
            3263190564384012888,
            PriceMath.tick_index_to_sqrt_price_x64(-22976),
            True
        )
        self.assertEqual(16588789, result)

    def test_get_token_a_from_liquidity_02(self):
        # in case
        result = LiquidityMath.get_token_a_from_liquidity(
            6638825,
            3263190564384012888,
            PriceMath.tick_index_to_sqrt_price_x64(-22976),
            False
        )
        self.assertEqual(16588789 - 1, result)

    def test_get_token_a_from_liquidity_03(self):
        result = LiquidityMath.get_token_a_from_liquidity(
            3402372134,
            PriceMath.tick_index_to_sqrt_price_x64(-19),
            PriceMath.tick_index_to_sqrt_price_x64(-19),
            True
        )
        self.assertEqual(0, result)

    def test_get_token_a_from_liquidity_04(self):
        result = LiquidityMath.get_token_a_from_liquidity(
            41191049234,
            PriceMath.tick_index_to_sqrt_price_x64(-592),
            PriceMath.tick_index_to_sqrt_price_x64(-589),
            True
        )
        self.assertEqual(6363475, result)

    def test_get_token_a_from_liquidity_05(self):
        result = LiquidityMath.get_token_a_from_liquidity(
            41191049234,
            PriceMath.tick_index_to_sqrt_price_x64(-589),
            PriceMath.tick_index_to_sqrt_price_x64(-592),
            True
        )
        self.assertEqual(6363475, result)

    def test_get_token_b_from_liquidity_01(self):
        result = LiquidityMath.get_token_b_from_liquidity(
            6638825,
            3263190564384012888,
            PriceMath.tick_index_to_sqrt_price_x64(-36864),
            True
        )
        self.assertEqual(123305, result)

    def test_get_token_b_from_liquidity_02(self):
        result = LiquidityMath.get_token_b_from_liquidity(
            6638825,
            3263190564384012888,
            PriceMath.tick_index_to_sqrt_price_x64(-36864),
            False
        )
        self.assertEqual(123305 - 1, result)

    def test_get_token_b_from_liquidity_03(self):
        result = LiquidityMath.get_token_b_from_liquidity(
            3402372134,
            PriceMath.tick_index_to_sqrt_price_x64(-21),
            PriceMath.tick_index_to_sqrt_price_x64(-19),
            True
        )
        self.assertEqual(339881, result)

    def test_get_token_b_from_liquidity_04(self):
        result = LiquidityMath.get_token_b_from_liquidity(
            41191049234,
            PriceMath.tick_index_to_sqrt_price_x64(-592),
            PriceMath.tick_index_to_sqrt_price_x64(-592),
            True
        )
        self.assertEqual(0, result)

    def test_get_token_b_from_liquidity_05(self):
        result = LiquidityMath.get_token_b_from_liquidity(
            3402372134,
            PriceMath.tick_index_to_sqrt_price_x64(-19),
            PriceMath.tick_index_to_sqrt_price_x64(-21),
            True
        )
        self.assertEqual(339881, result)

    def test_get_liquidity_from_token_a_01(self):
        # in case
        result = LiquidityMath.get_liquidity_from_token_a(
            3263190564384012888,
            PriceMath.tick_index_to_sqrt_price_x64(-22976),
            16588789
        )
        expected = 6638825
        self.assertEqual(expected, result)

    def test_get_liquidity_from_token_a_02(self):
        # out case (above)
        result = LiquidityMath.get_liquidity_from_token_a(
            PriceMath.tick_index_to_sqrt_price_x64(-21),
            PriceMath.tick_index_to_sqrt_price_x64(-19),
            0
        )
        expected = 0
        self.assertEqual(expected, result)

    def test_get_liquidity_from_token_a_03(self):
        # out case (above)
        result = LiquidityMath.get_liquidity_from_token_a(
            PriceMath.tick_index_to_sqrt_price_x64(-19),
            PriceMath.tick_index_to_sqrt_price_x64(-19),
            U64_MAX
        )
        expected = 0
        self.assertEqual(expected, result)

    def test_get_liquidity_from_token_a_04(self):
        # out case (below)
        result = LiquidityMath.get_liquidity_from_token_a(
            PriceMath.tick_index_to_sqrt_price_x64(-592),
            PriceMath.tick_index_to_sqrt_price_x64(-589),
            6363475
        )
        expected = 41191052885
        self.assertEqual(expected, result)

    def test_get_liquidity_from_token_b_01(self):
        # in case
        result = LiquidityMath.get_liquidity_from_token_b(
            PriceMath.tick_index_to_sqrt_price_x64(-36864),
            3263190564384012888,
            123305
        )
        expected = 6638830
        self.assertEqual(expected, result)

    def test_get_liquidity_from_token_b_02(self):
        # out case (above)
        result = LiquidityMath.get_liquidity_from_token_b(
            PriceMath.tick_index_to_sqrt_price_x64(-21),
            PriceMath.tick_index_to_sqrt_price_x64(-19),
            339881
        )
        expected = 3402380446
        self.assertEqual(expected, result)

    def test_get_liquidity_from_token_b_03(self):
        # out case (below)
        result = LiquidityMath.get_liquidity_from_token_b(
            PriceMath.tick_index_to_sqrt_price_x64(-592),
            PriceMath.tick_index_to_sqrt_price_x64(-589),
            0
        )
        expected = 0
        self.assertEqual(expected, result)

    def test_get_liquidity_from_token_b_04(self):
        # out case (below)
        result = LiquidityMath.get_liquidity_from_token_b(
            PriceMath.tick_index_to_sqrt_price_x64(-592),
            PriceMath.tick_index_to_sqrt_price_x64(-592),
            U64_MAX
        )
        expected = 0
        self.assertEqual(expected, result)


class PoolUtilTestCase(unittest.TestCase):
    def test_get_fee_rate_01(self):
        fee_rate = 10000
        result = PoolUtil.get_fee_rate(fee_rate)
        self.assertEqual(fee_rate, result.numerator)
        self.assertEqual(FEE_RATE_MUL_VALUE, result.denominator)

    def test_get_protocol_fee_rate_01(self):
        protocol_fee_rate = 300
        result = PoolUtil.get_protocol_fee_rate(protocol_fee_rate)
        self.assertEqual(protocol_fee_rate, result.numerator)
        self.assertEqual(PROTOCOL_FEE_RATE_MUL_VALUE, result.denominator)

    def test_is_reward_initialized_01(self):
        mint = Pubkey.from_string("11111111111111111111111111111111")
        vault = Pubkey.from_string("11111111111111111111111111111111")
        expected = False
        reward_info = WhirlpoolRewardInfo(mint, vault, Pubkey.default(), 0, 0)
        result = PoolUtil.is_reward_initialized(reward_info)
        self.assertEqual(expected, result)

    def test_is_reward_initialized_02(self):
        mint = Pubkey.from_string("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE")
        vault = Pubkey.from_string("11111111111111111111111111111111")
        expected = False
        reward_info = WhirlpoolRewardInfo(mint, vault, Pubkey.default(), 0, 0)
        result = PoolUtil.is_reward_initialized(reward_info)
        self.assertEqual(expected, result)

    def test_is_reward_initialized_03(self):
        mint = Pubkey.from_string("11111111111111111111111111111111")
        vault = Pubkey.from_string("2tU3tKvj7RBxEatryyMYTUxBoLSSWCQXsdv1X6yce4T2")
        expected = False
        reward_info = WhirlpoolRewardInfo(mint, vault, Pubkey.default(), 0, 0)
        result = PoolUtil.is_reward_initialized(reward_info)
        self.assertEqual(expected, result)

    def test_is_reward_initialized_04(self):
        mint = Pubkey.from_string("orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE")
        vault = Pubkey.from_string("2tU3tKvj7RBxEatryyMYTUxBoLSSWCQXsdv1X6yce4T2")
        expected = True
        reward_info = WhirlpoolRewardInfo(mint, vault, Pubkey.default(), 0, 0)
        result = PoolUtil.is_reward_initialized(reward_info)
        self.assertEqual(expected, result)


class PositionUtilTestCase(unittest.TestCase):
    def test_get_position_status_01(self):
        current = -65
        lower = -64
        upper = +64
        status = PositionUtil.get_position_status(current, lower, upper)
        self.assertEqual(PositionStatus.PriceIsBelowRange, status)

    def test_get_position_status_02(self):
        current = -64
        lower = -64
        upper = +64
        status = PositionUtil.get_position_status(current, lower, upper)
        self.assertEqual(PositionStatus.PriceIsInRange, status)

    def test_get_position_status_03(self):
        current = 0
        lower = -64
        upper = +64
        status = PositionUtil.get_position_status(current, lower, upper)
        self.assertEqual(PositionStatus.PriceIsInRange, status)

    def test_get_position_status_04(self):
        current = 63
        lower = -64
        upper = +64
        status = PositionUtil.get_position_status(current, lower, upper)
        self.assertEqual(PositionStatus.PriceIsInRange, status)

    def test_get_position_status_05(self):
        current = 64
        lower = -64
        upper = +64
        status = PositionUtil.get_position_status(current, lower, upper)
        self.assertEqual(PositionStatus.PriceIsAboveRange, status)

    def test_get_position_status_06(self):
        current = 65
        lower = -64
        upper = +64
        status = PositionUtil.get_position_status(current, lower, upper)
        self.assertEqual(PositionStatus.PriceIsAboveRange, status)


class WhirlpoolContextTestCase(unittest.TestCase):
    def test_whirlpool_context_01(self):
        connection = AsyncClient("https://api.mainnet-beta.solana.com")
        wallet = Keypair()
        ctx = WhirlpoolContext(ORCA_WHIRLPOOL_PROGRAM_ID, connection, wallet)
        self.assertEqual(ORCA_WHIRLPOOL_PROGRAM_ID, ctx.program_id)
        self.assertEqual(connection, ctx.connection)
        self.assertEqual(wallet, ctx.wallet)
        self.assertIsNotNone(ctx.fetcher)

    def test_whirlpool_context_02(self):
        connection = AsyncClient("https://api.mainnet-beta.solana.com")
        wallet = Keypair()
        fetcher = AccountFetcher(connection)
        ctx = WhirlpoolContext(ORCA_WHIRLPOOL_PROGRAM_ID, connection, wallet, fetcher)
        self.assertEqual(ORCA_WHIRLPOOL_PROGRAM_ID, ctx.program_id)
        self.assertEqual(connection, ctx.connection)
        self.assertEqual(wallet, ctx.wallet)
        self.assertEqual(fetcher, ctx.fetcher)


class SwapDirectionTestCase(unittest.TestCase):
    def test_a_to_b_01(self):
        self.assertEqual("SwapDirection.AtoB", str(SwapDirection.AtoB))

    def test_a_to_b_02(self):
        self.assertTrue(SwapDirection.AtoB.is_a_to_b)
        self.assertFalse(SwapDirection.AtoB.is_b_to_a)

    def test_a_to_b_03(self):
        self.assertTrue(SwapDirection.AtoB.is_price_down)
        self.assertFalse(SwapDirection.AtoB.is_price_up)

    def test_b_to_a_01(self):
        self.assertEqual("SwapDirection.BtoA", str(SwapDirection.BtoA))

    def test_b_to_a_02(self):
        self.assertFalse(SwapDirection.BtoA.is_a_to_b)
        self.assertTrue(SwapDirection.BtoA.is_b_to_a)

    def test_b_to_a_03(self):
        self.assertFalse(SwapDirection.BtoA.is_price_down)
        self.assertTrue(SwapDirection.BtoA.is_price_up)


class SpecifiedAmountTestCase(unittest.TestCase):
    def test_swap_input_01(self):
        self.assertEqual("SpecifiedAmount.SwapInput", str(SpecifiedAmount.SwapInput))

    def test_swap_input_02(self):
        self.assertTrue(SpecifiedAmount.SwapInput.is_swap_input)
        self.assertFalse(SpecifiedAmount.SwapInput.is_swap_output)

    def test_swap_input_03(self):
        self.assertTrue(SpecifiedAmount.SwapInput.is_a(SwapDirection.AtoB))
        self.assertFalse(SpecifiedAmount.SwapInput.is_b(SwapDirection.AtoB))
        self.assertFalse(SpecifiedAmount.SwapInput.is_a(SwapDirection.BtoA))
        self.assertTrue(SpecifiedAmount.SwapInput.is_b(SwapDirection.BtoA))

    def test_swap_output_01(self):
        self.assertEqual("SpecifiedAmount.SwapOutput", str(SpecifiedAmount.SwapOutput))

    def test_swap_output_02(self):
        self.assertFalse(SpecifiedAmount.SwapOutput.is_swap_input)
        self.assertTrue(SpecifiedAmount.SwapOutput.is_swap_output)

    def test_swap_output_03(self):
        self.assertFalse(SpecifiedAmount.SwapOutput.is_a(SwapDirection.AtoB))
        self.assertTrue(SpecifiedAmount.SwapOutput.is_b(SwapDirection.AtoB))
        self.assertTrue(SpecifiedAmount.SwapOutput.is_a(SwapDirection.BtoA))
        self.assertFalse(SpecifiedAmount.SwapOutput.is_b(SwapDirection.BtoA))


if __name__ == "__main__":
    unittest.main()
