import asyncio
import os
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient

from orca_whirlpool.accounts import AccountFinder
from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID, ORCA_WHIRLPOOLS_CONFIG

load_dotenv()
RPC_ENDPOINT_URL = os.getenv("RPC_ENDPOINT_URL")


async def main():
    connection = AsyncClient(RPC_ENDPOINT_URL)

    finder = AccountFinder(connection)
    orca_supported_whirlpools = await finder.find_whirlpools_by_whirlpools_config(
        ORCA_WHIRLPOOL_PROGRAM_ID,
        ORCA_WHIRLPOOLS_CONFIG,
    )

    for p in orca_supported_whirlpools:
        print(str(p.pubkey), str(p.whirlpools_config), str(p.token_mint_a), str(p.token_mint_b), p.tick_spacing)

    print(len(orca_supported_whirlpools), "pools found")

asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python esseintials_list_whirlpools.py
...
87pXxC5esd3W9qxZEVM2Sp67Tj9kw3B8SC5PdmMMftEz 2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ So11111111111111111111111111111111111111112 4nVrYKTgH3UtPMvnJSEqdMeEMyGU2YGC6XwSKTNy2UU2 64
8p97ModoCDDHjiqu8wEuRtqEtnmWUa2ZMQ43dVC2b2cC 2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ 2wme8EVkw8qsfSk2B3QeX4S64ac6wxHPXb3GrdckEkio EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 64
2511 pools found
"""