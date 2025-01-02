import dataclasses
from typing import Optional
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders import system_program
from spl.token.instructions import get_associated_token_address
from spl.token._layouts import MINT_LAYOUT, ACCOUNT_LAYOUT
from spl.token.constants import TOKEN_PROGRAM_ID, TOKEN_2022_PROGRAM_ID, WRAPPED_SOL_MINT, ACCOUNT_LEN
from spl.token import instructions as token_program
from ..transaction.types import Instruction
from ..transaction.transaction_builder import EMPTY_INSTRUCTION
from ..types.types import PublicKeyWithInstruction
from ..invariant import invariant


@dataclasses.dataclass(frozen=True)
class RawMintInfo:
    token_program_id: Pubkey
    mint_authority: Optional[Pubkey]
    supply: int
    decimals: int
    is_initialized: bool
    freeze_authority: Pubkey
    tlv_data: bytes


@dataclasses.dataclass(frozen=True)
class RawAccountInfo:
    token_program_id: Pubkey
    mint: Pubkey
    owner: Pubkey
    amount: int
    delegate: Optional[Pubkey]
    delegated_amount: int
    is_initialized: bool
    is_frozen: bool
    is_native: bool
    close_authority: Optional[Pubkey]
    tlv_data: bytes


class TokenUtil:
    # https://github.com/michaelhly/solana-py/blob/32119e6924d72cd2d605a949b28f2a366941d641/src/spl/token/core.py#L373
    @staticmethod
    def deserialize_account(data: bytes, program_id: Pubkey) -> Optional[RawAccountInfo]:
        if program_id == TOKEN_PROGRAM_ID:
            if len(data) == 165:
                pass
            else:
                return None
        elif program_id == TOKEN_2022_PROGRAM_ID:
            if len(data) == 165:
                pass
            elif len(data) >= 165+1 and data[165] == 2:
                pass
            else:
                return None
        else:
            return None

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
        is_native = decoded_data.is_native_option == 1
        is_frozen = decoded_data.state == 2

        if decoded_data.close_authority_option == 0:
            close_authority = None
        else:
            close_authority = Pubkey(decoded_data.owner)

        tlv_data = data[166:] if len(data) > 165+1 else b""

        return RawAccountInfo(
            token_program_id=program_id,
            mint=mint,
            owner=owner,
            amount=amount,
            delegate=delegate,
            delegated_amount=delegated_amount,
            is_initialized=is_initialized,
            is_frozen=is_frozen,
            is_native=is_native,
            close_authority=close_authority,
            tlv_data=tlv_data,
        )

    # https://github.com/michaelhly/solana-py/blob/32119e6924d72cd2d605a949b28f2a366941d641/src/spl/token/core.py#L343
    @staticmethod
    def deserialize_mint(data: bytes, program_id: Pubkey) -> Optional[RawMintInfo]:
        if program_id == TOKEN_PROGRAM_ID:
            if len(data) == 82:
                pass
            else:
                return None
        elif program_id == TOKEN_2022_PROGRAM_ID:
            if len(data) == 82:
                pass
            elif len(data) >= 165+1 and data[165] == 1:
                pass
            else:
                return None
        else:
            return None

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

        tlv_data = data[166:] if len(data) > 165+1 else b""

        return RawMintInfo(
            token_program_id=program_id,
            mint_authority=mint_authority,
            supply=supply,
            decimals=decimals,
            is_initialized=is_initialized,
            freeze_authority=freeze_authority,
            tlv_data=tlv_data,
        )

    @staticmethod
    def derive_ata(owner: Pubkey, mint: Pubkey, token_program_id: Pubkey = TOKEN_PROGRAM_ID) -> Pubkey:
        return get_associated_token_address(owner, mint, token_program_id)

    @staticmethod
    async def resolve_or_create_ata(
        connection: AsyncClient,
        owner: Pubkey,
        mint: Pubkey,
        wrapped_sol_amount: int = 0,
        funder: Pubkey = None,
        idempotent: bool = True,
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

        ata = TokenUtil.derive_ata(owner, mint, TOKEN_PROGRAM_ID)
        ata_2022 = TokenUtil.derive_ata(owner, mint, TOKEN_2022_PROGRAM_ID)

        res = await connection.get_multiple_accounts([
            mint,
            ata,
            ata_2022,
        ])

        fetched_mint = res.value[0]
        invariant(fetched_mint is not None)
        parsed_mint = TokenUtil.deserialize_mint(fetched_mint.data, fetched_mint.owner)
        invariant(parsed_mint is not None)
        token_program_id = parsed_mint.token_program_id

        fetched_ata = res.value[1]
        fetched_ata_2022 = res.value[2]

        # Token-2022 Program
        if token_program_id == TOKEN_2022_PROGRAM_ID:
            invariant(fetched_ata is None)
            if fetched_ata_2022 is not None:
                parsed_ata_2022 = TokenUtil.deserialize_account(fetched_ata_2022.data, fetched_ata_2022.owner)
                invariant(parsed_ata_2022.token_program_id == token_program_id, "parsed_account.token_program_id must be Token-2022")
                invariant(parsed_ata_2022.owner == owner, "parsed_account.owner == owner")
                invariant(parsed_ata_2022.mint == mint, "parsed_account.mint == mint")
                return PublicKeyWithInstruction(pubkey=ata_2022, instruction=EMPTY_INSTRUCTION)

            if idempotent:
                create_ata_2022_ix = token_program.create_idempotent_associated_token_account(funder, owner, mint, TOKEN_2022_PROGRAM_ID)
            else:
                create_ata_2022_ix = token_program.create_associated_token_account(funder, owner, mint, TOKEN_2022_PROGRAM_ID)
            return PublicKeyWithInstruction(
                pubkey=ata_2022,
                instruction=Instruction(
                    instructions=[create_ata_2022_ix],
                    cleanup_instructions=[],
                    signers=[],
                )
            )

        # Token Program
        invariant(token_program_id == TOKEN_PROGRAM_ID)
        invariant(fetched_ata_2022 is None)
        if fetched_ata is not None:
            parsed_ata = TokenUtil.deserialize_account(fetched_ata.data, fetched_ata.owner)
            invariant(parsed_ata.token_program_id == token_program_id, "parsed_account.token_program_id must be Token")
            invariant(parsed_ata.owner == owner, "parsed_account.owner == owner")
            invariant(parsed_ata.mint == mint, "parsed_account.mint == mint")
            return PublicKeyWithInstruction(pubkey=ata, instruction=EMPTY_INSTRUCTION)

        if idempotent:
            create_ata_ix = token_program.create_idempotent_associated_token_account(funder, owner, mint, TOKEN_PROGRAM_ID)
        else:
            create_ata_ix = token_program.create_associated_token_account(funder, owner, mint, TOKEN_PROGRAM_ID)
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
