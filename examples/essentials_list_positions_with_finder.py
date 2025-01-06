import asyncio
import os
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID, TOKEN_2022_PROGRAM_ID
from orca_whirlpool.accounts import AccountFinder
from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID

load_dotenv()
RPC_ENDPOINT_URL = os.getenv("RPC_ENDPOINT_URL")
MY_WALLET_PUBKEY = Pubkey.from_string("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6")


async def main():
    connection = AsyncClient(RPC_ENDPOINT_URL)

    finder = AccountFinder(connection)

    print("Old positions (Token program based NFT):")
    positions = await finder.find_positions_by_owner(
        ORCA_WHIRLPOOL_PROGRAM_ID,
        MY_WALLET_PUBKEY,
        token_program_id=TOKEN_PROGRAM_ID,
    )
    print(len(positions), "positions found")
    for p in positions:
        print("\t", str(p.pubkey), str(p.whirlpool), p.tick_lower_index, p.tick_upper_index)

    # now Orca UI create Token-2022 program based NFT
    # In SDK, you need to use open_position_with_token_extensions and close_position_with_token_extensions
    print("New positions (Token-2022 program based NFT):")
    positions = await finder.find_positions_by_owner(
        ORCA_WHIRLPOOL_PROGRAM_ID,
        MY_WALLET_PUBKEY,
        token_program_id=TOKEN_2022_PROGRAM_ID,
    )
    print(len(positions), "positions found")
    for p in positions:
        print("\t", str(p.pubkey), str(p.whirlpool), p.tick_lower_index, p.tick_upper_index)


asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python essentials_list_positions_with_finder.py

Old positions (Token program based NFT):
31 positions found
    2fcPp9nSnk5NHeHVrsEz3Kpv5QhcfPvMc4LgmajKpyz1 58svAxgvgc9yuYMvfiUoDVCfqao51kxB1nHsoMUcErrX -247040 -246784
    G3cVb8WfXoSNavoaZhXtAzfhNzyP7EfyvgXqhhuTBURA 7qbRF6YsyGuLUVs6Y1q64bdVrfe4ZcUUz1JRdoVNUJnm -443632 443632
    ADnY4Bnk5yM8RXKZ4Cjmx63SKUiwqQwNdW7D9VRpooyP 9vqYJjDUFecLL2xPUC4Rc7hyCtZ6iJ4mDiVZX7aFXoAe -132480 -118656
    ...

New positions (Token-2022 program based NFT):
5 positions found
    AmCrz7jWiywKtNiwJRp9vamTDHydRqbVHUqT977kdfEm 5Z66YYYaTmmx1R4mATAGLSc8aV4Vfy5tNdJQzk1GP9RF -443584 443584
    3hY9guUxBLY4ZQDcybx3wkXER3mFRgjNpQa3agJ1Ufrt CWjGo5jkduSW5LN5rxgiQ18vGnJJEKWPCXkpJGxKSQTH -427648 427648
    ...

"""