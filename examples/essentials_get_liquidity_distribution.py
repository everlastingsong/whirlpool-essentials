import asyncio
import os
from dotenv import load_dotenv
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

from orca_whirlpool.accounts import AccountFinder, AccountFetcher
from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID
from orca_whirlpool.utils import PoolUtil

load_dotenv()
RPC_ENDPOINT_URL = os.getenv("RPC_ENDPOINT_URL")


async def main():
    connection = AsyncClient(RPC_ENDPOINT_URL)

    whirlpool_pubkey = Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ")

    fetcher = AccountFetcher(connection)
    whirlpool = await fetcher.get_whirlpool(whirlpool_pubkey)
    finder = AccountFinder(connection)
    tick_arrays = await finder.find_tick_arrays_by_whirlpool(
        ORCA_WHIRLPOOL_PROGRAM_ID,
        whirlpool_pubkey,
    )

    liquidity_distribution = PoolUtil.get_liquidity_distribution(whirlpool, tick_arrays)

    for ld in liquidity_distribution:
        print(ld.tick_lower_index, ld.tick_upper_index, ld.liquidity)

asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python esseintials_list_liquidity_distribution.py
...
-12032 -10752 15859063093
-10752 13440 15514506269
13440 26240 15512612499
26240 29248 15531622772
29248 36800 15637755585
36800 138112 15512612499
138112 443584 15511072491
"""