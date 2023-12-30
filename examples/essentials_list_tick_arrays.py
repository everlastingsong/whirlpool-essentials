import asyncio
import os
from dotenv import load_dotenv
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

from orca_whirlpool.accounts import AccountFinder
from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID

load_dotenv()
RPC_ENDPOINT_URL = os.getenv("RPC_ENDPOINT_URL")


async def main():
    connection = AsyncClient(RPC_ENDPOINT_URL)

    whirlpool = Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ")

    finder = AccountFinder(connection)
    tick_arrays = await finder.find_tick_arrays_by_whirlpool(
        ORCA_WHIRLPOOL_PROGRAM_ID,
        whirlpool,
    )

    tick_arrays.sort(key=lambda ta: ta.start_tick_index)
    for ta in tick_arrays:
        print(str(ta.pubkey), ta.start_tick_index)

    print(len(tick_arrays), "tick arrays found")

asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python esseintials_list_tick_arrays.py
...
JBHjSQx3w3kV9uPJBGPKpbb76u4rdHTkpMZeofgyWdAD 135168
3CHNtXvVWSpjR2sbK4S4HpyahV9UwC6nzLBT75eNfF5X 439296
39 tick arrays found
"""