import asyncio
import os
from dotenv import load_dotenv
from typing import NamedTuple
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from spl.token.constants import TOKEN_PROGRAM_ID

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


async def main():
    connection = AsyncClient(RPC_ENDPOINT_URL)
    ctx = WhirlpoolContext(ORCA_WHIRLPOOL_PROGRAM_ID, connection, Keypair())

    token_program = TOKEN_PROGRAM_ID

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

        print("POSITION")
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

asyncio.run(main())

"""
SAMPLE OUTPUT:

$ python esseintials_list_positions.py
POSITION
  mint: EWMqkKRJfFd44493aGaz28V1evuVUmQhNKMkk45FieLK
  token_account: EabX3H5z8UZhEXZUA4z1z1pSkE6xFcWaCHTEc9i9Exkq
  position pubkey: FskauJ2rCscRCkeakA9btWjmr8CV4oU9xUePzQZhct7U
  whirlpool: 7wp9f3smjBFGk9AAAZkLJUrSLq8p1SUQ4uuNKrAp75AV
    token_a: SoLW9muuNQmEAoBws7CWfYQnXRXMVEG12cQhy6LE2Zf
    token_b: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
  liquidity: 1772979
  token_a(u64): 936466
  token_b(u64): 37117
POSITION
  mint: 7xL6mpE29vtLgntYEDEeawLm6WoeZMXKNYXZU7LGH2de
  token_account: 7jTmCxHpoLitqGxPfRXMdoRQQQmKQbWrAgUKmBZXoxke
  position pubkey: 9UP6D8rR9BVbVDqUkG8wkz9eZVBh69huKraaHehJyH3Z
  whirlpool: HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ
    token_a: So11111111111111111111111111111111111111112
    token_b: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
  liquidity: 6638825
  token_a(u64): 16705449
  token_b(u64): 119665
POSITION
  mint: MTyuSRevzwnSLW9s9NFoGWViQ63hnk3uR7Z19rpQhZA
  token_account: 69fd81NmuPnYSUe8UuQ7JtSU3xRoF7U5Q64ATfsbAmyY
  position pubkey: EEcRB8qMfTJxQurGajobwBdF2r8wQBMqEpB73cvwM9yG
  whirlpool: 2AEWSvUds1wsufnsDPCXjFsJCMJH5SNNm7fSF4kxys9a
    token_a: So11111111111111111111111111111111111111112
    token_b: 7dHbWXmci3dT8UFYWYZweBLXgycu7Y3iL6trKn1Y7ARj
  liquidity: 41191049234
  token_a(u64): 6363474
  token_b(u64): 0
"""