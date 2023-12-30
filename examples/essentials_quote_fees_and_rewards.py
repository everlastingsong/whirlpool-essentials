import asyncio
import os
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair

from orca_whirlpool.context import WhirlpoolContext
from orca_whirlpool.utils import DecimalUtil, PriceMath, PDAUtil, TickUtil, TickArrayUtil
from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID
from orca_whirlpool.quote import QuoteBuilder, CollectFeesQuoteParams, CollectRewardsQuoteParams


load_dotenv()
RPC_ENDPOINT_URL = os.getenv("RPC_ENDPOINT_URL")
POSITION_PUBKEY = Pubkey.from_string("2R17mPuvuZcryzUuqqnzxd1ZTRA5gFvhfcjM9Xwk6TqM")


async def main():
    # create Anchor client
    connection = AsyncClient(RPC_ENDPOINT_URL)
    ctx = WhirlpoolContext(ORCA_WHIRLPOOL_PROGRAM_ID, connection, Keypair())

    # get position
    position = await ctx.fetcher.get_position(POSITION_PUBKEY)
    whirlpool = await ctx.fetcher.get_whirlpool(position.whirlpool)
    token_a_decimal = (await ctx.fetcher.get_token_mint(whirlpool.token_mint_a)).decimals
    token_b_decimal = (await ctx.fetcher.get_token_mint(whirlpool.token_mint_b)).decimals
    print("whirlpool token_mint_a", whirlpool.token_mint_a)
    print("whirlpool token_mint_b", whirlpool.token_mint_b)
    print("whirlpool tick_spacing", whirlpool.tick_spacing)
    print("whirlpool tick_current_index", whirlpool.tick_current_index)
    print("whirlpool sqrt_price", whirlpool.sqrt_price)
    price = PriceMath.sqrt_price_x64_to_price(whirlpool.sqrt_price, token_a_decimal, token_b_decimal)
    print("whirlpool price", DecimalUtil.to_fixed(price, token_b_decimal))

    ta_lower_start_index = TickUtil.get_start_tick_index(position.tick_lower_index, whirlpool.tick_spacing)
    ta_upper_start_index = TickUtil.get_start_tick_index(position.tick_upper_index, whirlpool.tick_spacing)
    ta_lower_pubkey = PDAUtil.get_tick_array(ctx.program_id, position.whirlpool, ta_lower_start_index).pubkey
    ta_upper_pubkey = PDAUtil.get_tick_array(ctx.program_id, position.whirlpool, ta_upper_start_index).pubkey
    ta_lower = await ctx.fetcher.get_tick_array(ta_lower_pubkey)
    ta_upper = await ctx.fetcher.get_tick_array(ta_upper_pubkey)
    tick_lower = TickArrayUtil.get_tick_from_array(ta_lower, position.tick_lower_index, whirlpool.tick_spacing)
    tick_upper = TickArrayUtil.get_tick_from_array(ta_upper, position.tick_upper_index, whirlpool.tick_spacing)

    # quote fees
    quote_fees = QuoteBuilder.collect_fees(CollectFeesQuoteParams(
        whirlpool=whirlpool,
        position=position,
        tick_lower=tick_lower,
        tick_upper=tick_upper,
    ))
    print(quote_fees)

    # quote rewards
    quote_rewards = QuoteBuilder.collect_rewards(CollectRewardsQuoteParams(
        whirlpool=whirlpool,
        position=position,
        tick_lower=tick_lower,
        tick_upper=tick_upper,
    ))
    print(quote_rewards)

    # update
    latest_block_timestamp = await ctx.fetcher.get_latest_block_timestamp()
    print("latest", latest_block_timestamp)
    print("whirlpool timestamp", whirlpool.reward_last_updated_timestamp)

    quote_rewards2 = QuoteBuilder.collect_rewards(CollectRewardsQuoteParams(
        whirlpool=whirlpool,
        position=position,
        tick_lower=tick_lower,
        tick_upper=tick_upper,
        latest_block_timestamp=latest_block_timestamp.timestamp,
    ))
    print(quote_rewards2)

asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python essentials_swap.py
wallet pubkey r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6
whirlpool token_mint_a 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
whirlpool token_mint_b EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
whirlpool tick_spacing 64
whirlpool tick_current_index -116826
whirlpool sqrt_price 53604644321225494
whirlpool price 0.008444
token_account_a 6dM4iMgSei6zF9y3sqdgSJ2xwNXML5wk5QKhV4DqJPhu
token_account_b FbQdXCQgGQYj3xcGeryVVFjKCTsAuu53vmCRtmjQEqM5
tickarrays [4xM1zPj8ihLFUs2DvptGVZKkdACSZgNaa8zpBTApNk9G, CHVTbSXJ3W1XEjQXx7BhV2ZSfzmQcbZzKTGZa6ph6BoH, EE9AbRXbCKRGMeN6qAxxMUTEEPd1tQo67oYBQKkUNrfJ]
oracle 5HyJnjQ4XTSVXUS2Q8Ef6VCVwnXGnHE2WTwq7iSaZJez
TX signature 41nnMC8zCu7nycUPJ6zG4edEfMihV85i4iVBV2Th2XZTQiJYnsDVxCvsgM2giwnKxZSm9YHQLMJPxKv7RzdP2izE
"""