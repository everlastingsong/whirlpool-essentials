from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from .accounts.account_fetcher import AccountFetcher


class WhirlpoolContext:
    __program_id: Pubkey
    __connection: AsyncClient
    __wallet: Keypair
    __fetcher: AccountFetcher

    def __init__(self, program_id: Pubkey, connection: AsyncClient, wallet: Keypair, fetcher: AccountFetcher = None):
        if fetcher is None:
            fetcher = AccountFetcher(connection)
        self.__program_id = program_id
        self.__connection = connection
        self.__wallet = wallet
        self.__fetcher = fetcher

    @property
    def program_id(self):
        return self.__program_id

    @property
    def connection(self):
        return self.__connection

    @property
    def wallet(self):
        return self.__wallet

    @property
    def fetcher(self):
        return self.__fetcher
