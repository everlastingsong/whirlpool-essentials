from enum import Enum


class PositionStatus(str, Enum):
    PriceIsBelowRange = "Below Range"
    PriceIsAboveRange = "Above Range"
    PriceIsInRange = "In Range"


class SwapDirection(str, Enum):
    AtoB = "A to B"
    BtoA = "B to A"

    @property
    def is_a_to_b(self):
        return self == SwapDirection.AtoB

    @property
    def is_b_to_a(self):
        return self == SwapDirection.BtoA

    @property
    def is_price_down(self):
        return self.is_a_to_b

    @property
    def is_price_up(self):
        return self.is_b_to_a


class SpecifiedAmount(str, Enum):
    SwapInput = "Swap Input"
    SwapOutput = "Swap Output"

    @property
    def is_swap_input(self) -> bool:
        return self == SpecifiedAmount.SwapInput

    @property
    def is_swap_output(self) -> bool:
        return self == SpecifiedAmount.SwapOutput

    def is_a(self, direction: SwapDirection) -> bool:
        return self.is_swap_input == direction.is_a_to_b

    def is_b(self, direction: SwapDirection) -> bool:
        return not self.is_a(direction)


class TickArrayReduction(str, Enum):
    No = "No"
    Conservative = "Conservative"
    Aggressive = "Aggressive"


class RemainingAccountsType(str, Enum):
    TransferHookA = "TransferHookA"
    TransferHookB = "TransferHookB"
    TransferHookReward = "TransferHookReward"
    TransferHookInput = "TransferHookInput"
    TransferHookIntermediate = "TransferHookIntermediate"
    TransferHookOutput = "TransferHookOutput"
    SupplementalTickArrays = "SupplementalTickArrays"
    SupplementalTickArraysOne = "SupplementalTickArraysOne"
    SupplementalTickArraysTwo = "SupplementalTickArraysTwo"
