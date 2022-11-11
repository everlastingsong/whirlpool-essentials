from enum import Enum


class WhirlpoolErrorCode(str, Enum):
    pass


class MathErrorCode(WhirlpoolErrorCode):
    MultiplicationOverflow = "MultiplicationOverflow"
    MulDivOverflow = "MulDivOverflow"
    MultiplicationShiftRightOverflow = "MultiplicationShiftRightOverflow"
    DivideByZero = "DivideByZero"


class TokenErrorCode(WhirlpoolErrorCode):
    TokenMaxExceeded = "TokenMaxExceeded"
    TokenMinSubceeded = "TokenMinSubceeded"


class SwapErrorCode(WhirlpoolErrorCode):
    InvalidSqrtPriceLimitDirection = "InvalidSqrtPriceLimitDirection"
    SqrtPriceOutOfBounds = "SqrtPriceOutOfBounds"
    ZeroTradableAmount = "ZeroTradableAmount"
    AmountOutBelowMinimum = "AmountOutBelowMinimum"
    AmountInAboveMaximum = "AmountInAboveMaximum"
    TickArrayCrossingAboveMax = "TickArrayCrossingAboveMax"
    TickArrayIndexNotInitialized = "TickArrayIndexNotInitialized"
    TickArraySequenceInvalid = "TickArraySequenceInvalid"
    SqrtPriceMaxExceeded = "SqrtPriceMaxExceeded"
    SqrtPriceMinSubceeded = "SqrtPriceMinSubceeded"
    TickArray0MustBeInitialized = "TickArray0MustBeInitialized"


class WhirlpoolError(Exception):
    def __init__(self, error_code: WhirlpoolErrorCode, message: str = None):
        if message is not None:
            super().__init__(f"{str(error_code)}: {message}")
        else:
            super().__init__(str(error_code))
