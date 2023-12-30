from typing import Optional
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.signature import Signature
from solders import compute_budget
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment, Confirmed
from .types import Instruction, TransactionPayload

EMPTY_INSTRUCTION = Instruction([], [], [])

CONFIRM_TRANSACTION_CHECK_INTERVAL_SECOND = 1


class TransactionBuilder:
    def __init__(self, connection: AsyncClient, fee_payer: Keypair):
        self._connection = connection
        self._fee_payer = fee_payer
        self._instructions = []
        self._signers = []

    def set_compute_unit_limit(self, units: int):
        self._instructions.insert(0, Instruction(
            instructions=[compute_budget.set_compute_unit_limit(units)],
            cleanup_instructions=[],
            signers=[]
        ))

    def set_compute_unit_price(self, micro_lamports: int):
        self._instructions.insert(0, Instruction(
            instructions=[compute_budget.set_compute_unit_price(micro_lamports)],
            cleanup_instructions=[],
            signers=[]
        ))

    def add_instruction(self, instruction: Instruction) -> "TransactionBuilder":
        if not is_empty_instruction(instruction):
            self._instructions.append(instruction)
        return self

    def add_signer(self, signer: Keypair) -> "TransactionBuilder":
        self._signers.append(signer)
        return self

    def is_empty(self) -> bool:
        return len(self._instructions) == 0

    def pack_instructions(self, merge_cleanup_instructions: bool) -> Instruction:
        instructions = []
        cleanup_instructions = []
        signers = []
        for instruction in self._instructions:
            instructions.extend(instruction.instructions)
            cleanup_instructions = instruction.cleanup_instructions + cleanup_instructions
            signers.extend(instruction.signers)

        if merge_cleanup_instructions:
            instructions.extend(cleanup_instructions)
            cleanup_instructions = []

        return Instruction(
            instructions=instructions,
            cleanup_instructions=cleanup_instructions,
            signers=signers,
        )

    def build(self) -> TransactionPayload:
        packed = self.pack_instructions(True)

        return TransactionPayload(
            transaction=Transaction.new_with_payer(packed.instructions, self._fee_payer.pubkey()),
            signers=[self._fee_payer] + packed.signers + self._signers,
        )

    async def build_and_execute(self, commitment: Optional[Commitment] = Confirmed) -> Signature:
        payload = self.build()

        latest_blockhash = (await self._connection.get_latest_blockhash()).value

        tx = Transaction(payload.signers, payload.transaction.message, latest_blockhash.blockhash)
        signature = (await self._connection.send_raw_transaction(bytes(tx))).value
        await self._connection.confirm_transaction(
            signature,
            commitment,
            sleep_seconds=CONFIRM_TRANSACTION_CHECK_INTERVAL_SECOND,
            last_valid_block_height=latest_blockhash.last_valid_block_height
        )
        return signature


def is_empty_instruction(instruction: Instruction) -> bool:
    if len(instruction.instructions) > 0:
        return False
    if len(instruction.cleanup_instructions) > 0:
        return False
    if len(instruction.signers) > 0:
        return False
    return True
