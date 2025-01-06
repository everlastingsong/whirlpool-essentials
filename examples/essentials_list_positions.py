import asyncio
import os
from dotenv import load_dotenv
from typing import NamedTuple
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from spl.token.constants import TOKEN_PROGRAM_ID, TOKEN_2022_PROGRAM_ID

from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID
from orca_whirlpool.context import WhirlpoolContext
from orca_whirlpool.utils import TokenUtil, LiquidityMath, PriceMath, PDAUtil, PositionUtil

load_dotenv()
RPC_ENDPOINT_URL = os.getenv("RPC_ENDPOINT_URL")
MY_WALLET_PUBKEY = Pubkey.from_string("r21Gamwd9DtyjHeGywsneoQYR39C1VDwrw7tWxHAwh6")


class PositionRelatedAccounts(NamedTuple):
    mint: Pubkey
    token_account: Pubkey
    position: Pubkey


async def list_positions(ctx: WhirlpoolContext, token_program: Pubkey):
    # list all token accounts
    res = await ctx.connection.get_token_accounts_by_owner(
        MY_WALLET_PUBKEY,
        TokenAccountOpts(program_id=token_program, encoding="base64")
    )
    token_accounts = res.value

    candidates = []
    for token_account in token_accounts:
        pubkey = token_account.pubkey
        parsed = TokenUtil.deserialize_account(token_account.account.data, token_program)

        # maybe NFT
        if parsed.amount == 1:
            # derive position address
            position = PDAUtil.get_position(ORCA_WHIRLPOOL_PROGRAM_ID, parsed.mint).pubkey
            candidates.append(PositionRelatedAccounts(parsed.mint, pubkey, position))

    # make cache
    position_pubkeys = list(map(lambda c: c.position, candidates))
    fetched = await ctx.fetcher.list_positions(position_pubkeys, True)
    whirlpool_pubkeys = [fetched[i].whirlpool for i in range(len(fetched)) if fetched[i] is not None]
    await ctx.fetcher.list_whirlpools(whirlpool_pubkeys, True)

    for position, accounts in zip(fetched, candidates):
        if position is None:
            continue

        # fetch from cache
        whirlpool = await ctx.fetcher.get_whirlpool(position.whirlpool)
        # calc token amounts
        amounts = LiquidityMath.get_token_amounts_from_liquidity(
            position.liquidity,
            whirlpool.sqrt_price,
            PriceMath.tick_index_to_sqrt_price_x64(position.tick_lower_index),
            PriceMath.tick_index_to_sqrt_price_x64(position.tick_upper_index),
            False
        )
        # get status
        status = PositionUtil.get_position_status(
            whirlpool.tick_current_index,
            position.tick_lower_index,
            position.tick_upper_index
        )

        print("  mint:", accounts.mint)
        print("  token_account:", accounts.token_account)
        print("  position pubkey:", accounts.position)
        print("  whirlpool:", position.whirlpool)
        print("    token_a:", whirlpool.token_mint_a)
        print("    token_b:", whirlpool.token_mint_b)
        print("  liquidity:", position.liquidity)
        print("  token_a(u64):", amounts.token_a)
        print("  token_b(u64):", amounts.token_b)
        print("  status:", status)
        print("")


async def main():
    connection = AsyncClient(RPC_ENDPOINT_URL)
    ctx = WhirlpoolContext(ORCA_WHIRLPOOL_PROGRAM_ID, connection, Keypair())

    print("Old positions (Token program based NFT):")
    await list_positions(ctx, TOKEN_PROGRAM_ID)

    # now Orca UI create Token-2022 program based NFT
    # In SDK, you need to use open_position_with_token_extensions and close_position_with_token_extensions
    print("New positions (Token-2022 program based NFT):")
    await list_positions(ctx, TOKEN_2022_PROGRAM_ID)


asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python esseintials_list_positions.py

Old positions (Token program based NFT):
  mint: 8dBM2MtusX9AM75LC71yfjGuiwg14zeyaRCq1GLNK66p
  token_account: BdMLynUHb4PQJuDVujp8Yf1kuWi8dfwn1CMtQJkeZoYi
  position pubkey: 2fcPp9nSnk5NHeHVrsEz3Kpv5QhcfPvMc4LgmajKpyz1
  whirlpool: 58svAxgvgc9yuYMvfiUoDVCfqao51kxB1nHsoMUcErrX
    token_a: 7TyWPxzcE3MD7wnL79g5aVWjSngUZSvu7brqkews3nVc
    token_b: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
  liquidity: 179542253
  token_a(u64): 0
  token_b(u64): 9
  status: PositionStatus.PriceIsAboveRange

  mint: 9EerSewxNYNw6QjzdJg1qKL8ndr3ETn2ifEJbYahvr6w
  token_account: Exz8b7fveyADrrTP7vScJ7953LLwJRn1k7HVXe8kgkuB
  position pubkey: G3cVb8WfXoSNavoaZhXtAzfhNzyP7EfyvgXqhhuTBURA
  whirlpool: 7qbRF6YsyGuLUVs6Y1q64bdVrfe4ZcUUz1JRdoVNUJnm
    token_a: So11111111111111111111111111111111111111112
    token_b: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
  liquidity: 68263
  token_a(u64): 147740
  token_b(u64): 31540
  status: PositionStatus.PriceIsInRange

  ...

New positions (Token-2022 program based NFT):
  mint: DrPMQFDLvvKKfYB1kcSPhELMYnyH6YzqnePwGkJ51QZp
  token_account: FVGXmdLNPm5NpH7MaMNQbwXGkk8SEs3K8bnTXTHjrqKM
  position pubkey: AmCrz7jWiywKtNiwJRp9vamTDHydRqbVHUqT977kdfEm
  whirlpool: 5Z66YYYaTmmx1R4mATAGLSc8aV4Vfy5tNdJQzk1GP9RF
    token_a: orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE
    token_b: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
  liquidity: 18
  token_a(u64): 8
  token_b(u64): 36
  status: PositionStatus.PriceIsInRange

  mint: BtTcJahunGVVfkY4T81Vxk9Z9sB3yH1a7jR6LvXQcCjU
  token_account: 3x6cYe1SasKGAZwx342Mp8pL6PbJrCYZjTR1MWk98ZP3
  position pubkey: 3hY9guUxBLY4ZQDcybx3wkXER3mFRgjNpQa3agJ1Ufrt
  whirlpool: CWjGo5jkduSW5LN5rxgiQ18vGnJJEKWPCXkpJGxKSQTH
    token_a: So11111111111111111111111111111111111111112
    token_b: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
  liquidity: 39483
  token_a(u64): 85822
  token_b(u64): 18164
  status: PositionStatus.PriceIsInRange
  
  ...

"""