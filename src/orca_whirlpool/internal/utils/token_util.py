from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders import system_program
from spl.token.instructions import get_associated_token_address
from spl.token.core import MintInfo, AccountInfo
from spl.token._layouts import MINT_LAYOUT, ACCOUNT_LAYOUT
from spl.token.constants import TOKEN_PROGRAM_ID, WRAPPED_SOL_MINT, ACCOUNT_LEN
from spl.token import instructions as token_program
from ..transaction.types import Instruction
from ..transaction.transaction_builder import EMPTY_INSTRUCTION
from ..types.types import PublicKeyWithInstruction
from ..invariant import invariant


class TokenUtil:
    # https://github.com/michaelhly/solana-py/blob/32119e6924d72cd2d605a949b28f2a366941d641/src/spl/token/core.py#L373
    @staticmethod
    def deserialize_account(data: bytes):
        decoded_data = ACCOUNT_LAYOUT.parse(data)

        mint = Pubkey(decoded_data.mint)
        owner = Pubkey(decoded_data.owner)
        amount = decoded_data.amount

        if decoded_data.delegate_option == 0:
            delegate = None
            delegated_amount = 0
        else:
            delegate = Pubkey(decoded_data.delegate)
            delegated_amount = decoded_data.delegated_amount

        is_initialized = decoded_data.state != 0
        is_frozen = decoded_data.state == 2

        if decoded_data.is_native_option == 1:
            rent_exempt_reserve = decoded_data.is_native
            is_native = True
        else:
            rent_exempt_reserve = None
            is_native = False

        if decoded_data.close_authority_option == 0:
            close_authority = None
        else:
            close_authority = Pubkey(decoded_data.owner)

        return AccountInfo(
            mint,
            owner,
            amount,
            delegate,
            delegated_amount,
            is_initialized,
            is_frozen,
            is_native,
            rent_exempt_reserve,
            close_authority,
        )

    # https://github.com/michaelhly/solana-py/blob/32119e6924d72cd2d605a949b28f2a366941d641/src/spl/token/core.py#L343
    @staticmethod
    def deserialize_mint(data: bytes) -> MintInfo:
        decoded_data = MINT_LAYOUT.parse(data)
        decimals = decoded_data.decimals

        if decoded_data.mint_authority_option == 0:
            mint_authority = None
        else:
            mint_authority = Pubkey(decoded_data.mint_authority)

        supply = decoded_data.supply
        is_initialized = decoded_data.is_initialized != 0

        if decoded_data.freeze_authority_option == 0:
            freeze_authority = None
        else:
            freeze_authority = Pubkey(decoded_data.freeze_authority)

        return MintInfo(mint_authority, supply, decimals, is_initialized, freeze_authority)

    @staticmethod
    def derive_ata(owner: Pubkey, mint: Pubkey) -> Pubkey:
        return get_associated_token_address(owner, mint)

    @staticmethod
    async def resolve_or_create_ata(
        connection: AsyncClient,
        owner: Pubkey,
        mint: Pubkey,
        wrapped_sol_amount: int = 0,
        funder: Pubkey = None
    ) -> PublicKeyWithInstruction:
        if funder is None:
            funder = owner

        if mint == WRAPPED_SOL_MINT:
            return await TokenUtil.prepare_wrapped_sol_token_account(
                connection,
                owner,
                wrapped_sol_amount,
                funder,
            )

        ata = TokenUtil.derive_ata(owner, mint)
        res = await connection.get_account_info(ata)
        if res.value is not None:
            token_account = TokenUtil.deserialize_account(res.value.data)
            invariant(token_account.owner == owner, "token_account.owner == owner")
            invariant(token_account.mint == mint, "token_account.mint == mint")
            return PublicKeyWithInstruction(pubkey=ata, instruction=EMPTY_INSTRUCTION)

        create_ata_ix = token_program.create_associated_token_account(funder, owner, mint)
        return PublicKeyWithInstruction(
            pubkey=ata,
            instruction=Instruction(
                instructions=[create_ata_ix],
                cleanup_instructions=[],
                signers=[],
            )
        )

    @staticmethod
    async def prepare_wrapped_sol_token_account(
        connection: AsyncClient,
        owner: Pubkey,
        lamports: int,
        funder: Pubkey = None,
    ) -> PublicKeyWithInstruction:
        if funder is None:
            funder = owner

        wsol_token_account = Keypair()
        rent_lamports = (await connection.get_minimum_balance_for_rent_exemption(ACCOUNT_LEN)).value

        create_account_ix = system_program.create_account(system_program.CreateAccountParams(
            from_pubkey=funder,
            to_pubkey=wsol_token_account.pubkey(),
            lamports=rent_lamports + lamports,
            space=ACCOUNT_LEN,
            owner=TOKEN_PROGRAM_ID
        ))

        initialize_account_ix = token_program.initialize_account(token_program.InitializeAccountParams(
            program_id=TOKEN_PROGRAM_ID,
            account=wsol_token_account.pubkey(),
            mint=WRAPPED_SOL_MINT,
            owner=owner
        ))

        close_account_ix = token_program.close_account(token_program.CloseAccountParams(
            program_id=TOKEN_PROGRAM_ID,
            account=wsol_token_account.pubkey(),
            dest=funder,
            owner=owner,
            signers=[]
        ))

        return PublicKeyWithInstruction(
            pubkey=wsol_token_account.pubkey(),
            instruction=Instruction(
                instructions=[create_account_ix, initialize_account_ix],  # create instructions
                cleanup_instructions=[close_account_ix],  # delete instructions
                signers=[wsol_token_account],
            )
        )
