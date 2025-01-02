import asyncio
import os
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from orca_whirlpool.accounts import AccountFinder
from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID

load_dotenv()
RPC_ENDPOINT_URL = os.getenv("RPC_ENDPOINT_URL")
MY_WALLET_PUBKEY = Pubkey.from_string("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6")


async def main():
    connection = AsyncClient(RPC_ENDPOINT_URL)

    finder = AccountFinder(connection)
    positions = await finder.find_positions_by_owner(
        ORCA_WHIRLPOOL_PROGRAM_ID,
        MY_WALLET_PUBKEY,
        token_program_id=TOKEN_PROGRAM_ID,
    )

    for p in positions:
        print(str(p.pubkey), str(p.whirlpool), p.tick_lower_index, p.tick_upper_index)

    print(len(positions), "positions found")

asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python essentials_list_positions_with_finder.py
...
Aky9xQo1mcF5DZD5QC6aDDjGem2m6T56qvpZ5h3YjCg1 FAbwB8VgdgSGty5E8dnmNbu5PZnQcvSuLnboJVpw1Rty -443584 443584
nJpNKGkrS7BKrRNwxChfMQrRJ7G2TfUy4W1nVbNVRTk 7qbRF6YsyGuLUVs6Y1q64bdVrfe4ZcUUz1JRdoVNUJnm -443632 443632
AjS5LMLMVxDZ58vHBrXSWJpCf45ALXuPQGFg6ZznhUUg 4fuUiYxTQ6QCrdSq9ouBYcTM7bqSwYTSyLueGZLTy4T4 -7 0
AGJTqkDgLwPk1JkT9eCK4qS3jUE5rtDcrrb5DtHydePF BLihCrV7e6qwkTNJyVyGbnWKNs8x9Wt45qrRtauGrtHj 133120 146368
51 positions found
"""