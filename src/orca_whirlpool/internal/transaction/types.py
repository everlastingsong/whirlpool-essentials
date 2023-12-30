import dataclasses
from typing import List
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.instruction import Instruction as TransactionInstruction


@dataclasses.dataclass(frozen=True)
class Instruction:
    instructions: List[TransactionInstruction]
    cleanup_instructions: List[TransactionInstruction]
    signers: List[Keypair]


@dataclasses.dataclass(frozen=True)
class TransactionPayload:
    transaction: Transaction
    signers: List[Keypair]
