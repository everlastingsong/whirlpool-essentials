![DALL·E 2023-12-31 02 44 53 - A cute manga-style illustration in a 16_9 aspect ratio, featuring a whirlpool and an orca, representing the Python programming language  The whirlpool](https://github.com/everlastingsong/whirlpool-essentials/assets/98769788/801912c7-c35b-43a2-8e9e-280f4ff66cf7)

# Whirlpool Essentials
Whirlpool Essentials is a core library to interacting with Orca Whirlpool Program in Python.

## Documentation
* [pdoc for Whirlpool Essentials](https://everlastingsong.github.io/whirlpool-essentials/orca_whirlpool/index.html)

## Dependencies
This library have been tested in the following environment.

* Python: 3.10.6
* solders: 0.21.0
* solana: 0.35.1
* anchorpy: 0.20.1

## Installation
```commandline
pip install solana solders anchorpy
```
```commandline
pip install whirlpool-essentials
```

## Important Notes
### V2 instructions and TokenExtensions
Whirlpool Essentials can handle v2 instructions with `WhirlpoolIx`.
HOWEVER the quote functions cannot handle `TransferFee` extension yet.
So please ensure that input and output token don't use `TransferFee` extension.
If its fee rate is zero, it can be ignored. (e.g. `PYUSD`)

### General topics
- Whirlpool Essentials is NOT included in Orca's official SDK list, so the update may be delayed.
- Please use this package at your own risk.

## Sample
### Get SOL/USDC Whirlpool Price
```
import asyncio

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair

from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID
from orca_whirlpool.context import WhirlpoolContext
from orca_whirlpool.utils import PriceMath, DecimalUtil

SOL_USDC_8_WHIRLPOOL_PUBKEY = Pubkey.from_string("7qbRF6YsyGuLUVs6Y1q64bdVrfe4ZcUUz1JRdoVNUJnm")

async def main():
    connection = AsyncClient(RPC_ENDPOINT_URL)
    ctx = WhirlpoolContext(ORCA_WHIRLPOOL_PROGRAM_ID, connection, Keypair())

    # get SOL/USDC(ts=8) whirlpool
    whirlpool_pubkey = SOL_USDC_8_WHIRLPOOL_PUBKEY
    whirlpool = await ctx.fetcher.get_whirlpool(whirlpool_pubkey)
    decimals_a = (await ctx.fetcher.get_token_mint(whirlpool.token_mint_a)).decimals  # SOL_DECIMAL
    decimals_b = (await ctx.fetcher.get_token_mint(whirlpool.token_mint_b)).decimals  # USDC_DECIMAL

    print("whirlpool token_mint_a", whirlpool.token_mint_a)
    print("whirlpool token_mint_b", whirlpool.token_mint_b)
    print("whirlpool tick_spacing", whirlpool.tick_spacing)
    print("whirlpool tick_current_index", whirlpool.tick_current_index)
    print("whirlpool sqrt_price", whirlpool.sqrt_price)
    price = PriceMath.sqrt_price_x64_to_price(whirlpool.sqrt_price, decimals_a, decimals_b)
    print("whirlpool price", DecimalUtil.to_fixed(price, decimals_b))

asyncio.run(main())
```

### Get Liquidity Distribution of SOL/USDC Whirlpool
```
import asyncio
import os

from dotenv import load_dotenv
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

from orca_whirlpool.accounts import AccountFinder, AccountFetcher
from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID
from orca_whirlpool.utils import PoolUtil

async def main():
    connection = AsyncClient(RPC_ENDPOINT_URL)
    whirlpool_pubkey = Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ")

    # get liquidity distribution
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
```