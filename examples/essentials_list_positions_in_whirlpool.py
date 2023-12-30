import asyncio
import os
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from orca_whirlpool.accounts import AccountFinder
from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID

load_dotenv()
RPC_ENDPOINT_URL = os.getenv("RPC_ENDPOINT_URL")


async def main():
    connection = AsyncClient(RPC_ENDPOINT_URL)

    whirlpool = Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ")

    finder = AccountFinder(connection)
    positions = await finder.find_positions_by_whirlpool(
        ORCA_WHIRLPOOL_PROGRAM_ID,
        whirlpool
    )

    for p in positions:
        print(str(p.pubkey), str(p.whirlpool), p.tick_lower_index, p.tick_upper_index)

    print(len(positions), "positions found")

asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python essentials_list_positions_in_whirlpool.py
...
5Btbhy7zpqYLiaau2xqWGEEWzYEiwdYnnKvxjQvpyFEc HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ -25472 -23232
FvkVQSB5z2hj4JfxU8YueLSknpsgjUS3fb8Pmm5UG7tU HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ -37888 -37376
HBJRn8TNqGvVhWkzpTYHrWYH19S5VJgCTg4tfX7rZJch HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ -26496 -17920
1612 positions found
"""