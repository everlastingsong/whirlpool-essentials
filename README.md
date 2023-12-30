# Whirlpool Essentials

Whirlpool Essentials is a core library to interacting with Orca Whirlpool Program in Python.

## Dependencies
This library have been tested in the following environment.

* Python: 3.10.6
* solders: 0.18.1
* solana: 0.30.2
* anchorpy: 0.18.0

## Installation
```commandline
pip install solana solders anchorpy
```
```commandline
pip install whirlpool-essentials
```

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
    # create client
    connection = AsyncClient("https://api.mainnet-beta.solana.com")
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