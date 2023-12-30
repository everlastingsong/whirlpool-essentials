import dataclasses
from solders.pubkey import Pubkey
from ..transaction.types import Instruction


@dataclasses.dataclass(frozen=True)
class TokenAmounts:
    token_a: int
    token_b: int


@dataclasses.dataclass(frozen=True)
class PDA:
    pubkey: Pubkey
    bump: int


@dataclasses.dataclass(frozen=True)
class PublicKeyWithInstruction:
    pubkey: Pubkey
    instruction: Instruction


@dataclasses.dataclass(frozen=True)
class BlockTimestamp:
    slot: int
    timestamp: int
