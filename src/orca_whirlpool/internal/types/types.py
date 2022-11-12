import dataclasses
from solana.publickey import PublicKey
from ..transaction.types import Instruction


@dataclasses.dataclass(frozen=True)
class TokenAmounts:
    token_a: int
    token_b: int


@dataclasses.dataclass(frozen=True)
class PDA:
    pubkey: PublicKey
    bump: int


@dataclasses.dataclass(frozen=True)
class PublicKeyWithInstruction:
    pubkey: PublicKey
    instruction: Instruction


@dataclasses.dataclass(frozen=True)
class BlockTimestamp:
    slot: int
    timestamp: int
