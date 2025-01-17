from solders.pubkey import Pubkey


class OrcaWhirlpoolsConfig:
    SOLANA_MAINNET = Pubkey.from_string("2LecshUwdy9xi7meFgHtFJQNSKk4KdTrcpvaB56dP2NQ")
    SOLANA_DEVNET = Pubkey.from_string("FcrweFY1G9HJAHG5inkGB6pKg1HZ6x9UC2WioAfWrGkR")
    ECLIPSE_MAINNET = Pubkey.from_string("FVG4oDbGv16hqTUbovjyGmtYikn6UBEnazz6RVDMEFwv")
    ECLIPSE_TESTNET = Pubkey.from_string("FPydDjRdZu9sT7HVd6ANhfjh85KLq21Pefr5YWWMRPFp")


class OrcaWhirlpoolsConfigExtension:
    SOLANA_MAINNET = Pubkey.from_string("777H5H3Tp9U11uRVRzFwM8BinfiakbaLT8vQpeuhvEiH")
    SOLANA_DEVNET = Pubkey.from_string("475EJ7JqnRpVLoFVzp2ruEYvWWMCf6Z8KMWRujtXXNSU")
    ECLIPSE_MAINNET = Pubkey.from_string("9VrJciULifYcwu2CL8nbXdw4deqQgmv7VTzidwgQYBmm")
    ECLIPSE_TESTNET = Pubkey.from_string("6gUEB962oFdZtwoVyXNya9TfGWnBEbYNYt8UdvzT6PSf")


DEFAULT_PUBKEY = Pubkey.from_string("11111111111111111111111111111111")

# https://github.com/orca-so/whirlpools/blob/7b9ec35/sdk/src/types/public/constants.ts
ORCA_WHIRLPOOL_PROGRAM_ID = Pubkey.from_string("whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc")
ORCA_WHIRLPOOL_NFT_UPDATE_AUTHORITY = Pubkey.from_string("3axbTs2z5GBy6usVbNVoqEgZMng3vZvMnAoX29BFfwhr")
METAPLEX_METADATA_PROGRAM_ID = Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")

ORCA_WHIRLPOOLS_CONFIG = OrcaWhirlpoolsConfig()
ORCA_WHIRLPOOLS_CONFIG_EXTENSION = OrcaWhirlpoolsConfigExtension()

NUM_REWARDS = 3
TICK_ARRAY_SIZE = 88
MAX_SWAP_TICK_ARRAYS = 3
POSITION_BUNDLE_SIZE = 256

MIN_TICK_INDEX = -443636
MAX_TICK_INDEX = +443636

MIN_SQRT_PRICE = 4295048016
MAX_SQRT_PRICE = 79226673515401279992447579055

U64_MAX = 18446744073709551615

FEE_RATE_MUL_VALUE = 10**6
PROTOCOL_FEE_RATE_MUL_VALUE = 10**4

ACCOUNT_SIZE_WHIRLPOOLS_CONFIG = 108
ACCOUNT_SIZE_FEE_TIER = 44
ACCOUNT_SIZE_WHIRLPOOL = 653
ACCOUNT_SIZE_TICK_ARRAY = 9988
ACCOUNT_SIZE_POSITION = 216
ACCOUNT_SIZE_POSITION_BUNDLE = 136
ACCOUNT_SIZE_WHIRLPOOLS_CONFIG_EXTENSION = 616
ACCOUNT_SIZE_TOKEN_BADGE = 200
