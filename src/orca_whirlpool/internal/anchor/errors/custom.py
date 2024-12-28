import typing
from anchorpy.error import ProgramError


class InvalidEnum(ProgramError):
    def __init__(self) -> None:
        super().__init__(6000, "Enum value could not be converted")

    code = 6000
    name = "InvalidEnum"
    msg = "Enum value could not be converted"


class InvalidStartTick(ProgramError):
    def __init__(self) -> None:
        super().__init__(6001, "Invalid start tick index provided.")

    code = 6001
    name = "InvalidStartTick"
    msg = "Invalid start tick index provided."


class TickArrayExistInPool(ProgramError):
    def __init__(self) -> None:
        super().__init__(6002, "Tick-array already exists in this whirlpool")

    code = 6002
    name = "TickArrayExistInPool"
    msg = "Tick-array already exists in this whirlpool"


class TickArrayIndexOutofBounds(ProgramError):
    def __init__(self) -> None:
        super().__init__(6003, "Attempt to search for a tick-array failed")

    code = 6003
    name = "TickArrayIndexOutofBounds"
    msg = "Attempt to search for a tick-array failed"


class InvalidTickSpacing(ProgramError):
    def __init__(self) -> None:
        super().__init__(6004, "Tick-spacing is not supported")

    code = 6004
    name = "InvalidTickSpacing"
    msg = "Tick-spacing is not supported"


class ClosePositionNotEmpty(ProgramError):
    def __init__(self) -> None:
        super().__init__(6005, "Position is not empty It cannot be closed")

    code = 6005
    name = "ClosePositionNotEmpty"
    msg = "Position is not empty It cannot be closed"


class DivideByZero(ProgramError):
    def __init__(self) -> None:
        super().__init__(6006, "Unable to divide by zero")

    code = 6006
    name = "DivideByZero"
    msg = "Unable to divide by zero"


class NumberCastError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6007, "Unable to cast number into BigInt")

    code = 6007
    name = "NumberCastError"
    msg = "Unable to cast number into BigInt"


class NumberDownCastError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6008, "Unable to down cast number")

    code = 6008
    name = "NumberDownCastError"
    msg = "Unable to down cast number"


class TickNotFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6009, "Tick not found within tick array")

    code = 6009
    name = "TickNotFound"
    msg = "Tick not found within tick array"


class InvalidTickIndex(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6010, "Provided tick index is either out of bounds or uninitializable"
        )

    code = 6010
    name = "InvalidTickIndex"
    msg = "Provided tick index is either out of bounds or uninitializable"


class SqrtPriceOutOfBounds(ProgramError):
    def __init__(self) -> None:
        super().__init__(6011, "Provided sqrt price out of bounds")

    code = 6011
    name = "SqrtPriceOutOfBounds"
    msg = "Provided sqrt price out of bounds"


class LiquidityZero(ProgramError):
    def __init__(self) -> None:
        super().__init__(6012, "Liquidity amount must be greater than zero")

    code = 6012
    name = "LiquidityZero"
    msg = "Liquidity amount must be greater than zero"


class LiquidityTooHigh(ProgramError):
    def __init__(self) -> None:
        super().__init__(6013, "Liquidity amount must be less than i64::MAX")

    code = 6013
    name = "LiquidityTooHigh"
    msg = "Liquidity amount must be less than i64::MAX"


class LiquidityOverflow(ProgramError):
    def __init__(self) -> None:
        super().__init__(6014, "Liquidity overflow")

    code = 6014
    name = "LiquidityOverflow"
    msg = "Liquidity overflow"


class LiquidityUnderflow(ProgramError):
    def __init__(self) -> None:
        super().__init__(6015, "Liquidity underflow")

    code = 6015
    name = "LiquidityUnderflow"
    msg = "Liquidity underflow"


class LiquidityNetError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6016, "Tick liquidity net underflowed or overflowed")

    code = 6016
    name = "LiquidityNetError"
    msg = "Tick liquidity net underflowed or overflowed"


class TokenMaxExceeded(ProgramError):
    def __init__(self) -> None:
        super().__init__(6017, "Exceeded token max")

    code = 6017
    name = "TokenMaxExceeded"
    msg = "Exceeded token max"


class TokenMinSubceeded(ProgramError):
    def __init__(self) -> None:
        super().__init__(6018, "Did not meet token min")

    code = 6018
    name = "TokenMinSubceeded"
    msg = "Did not meet token min"


class MissingOrInvalidDelegate(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6019, "Position token account has a missing or invalid delegate"
        )

    code = 6019
    name = "MissingOrInvalidDelegate"
    msg = "Position token account has a missing or invalid delegate"


class InvalidPositionTokenAmount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6020, "Position token amount must be 1")

    code = 6020
    name = "InvalidPositionTokenAmount"
    msg = "Position token amount must be 1"


class InvalidTimestampConversion(ProgramError):
    def __init__(self) -> None:
        super().__init__(6021, "Timestamp should be convertible from i64 to u64")

    code = 6021
    name = "InvalidTimestampConversion"
    msg = "Timestamp should be convertible from i64 to u64"


class InvalidTimestamp(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6022, "Timestamp should be greater than the last updated timestamp"
        )

    code = 6022
    name = "InvalidTimestamp"
    msg = "Timestamp should be greater than the last updated timestamp"


class InvalidTickArraySequence(ProgramError):
    def __init__(self) -> None:
        super().__init__(6023, "Invalid tick array sequence provided for instruction.")

    code = 6023
    name = "InvalidTickArraySequence"
    msg = "Invalid tick array sequence provided for instruction."


class InvalidTokenMintOrder(ProgramError):
    def __init__(self) -> None:
        super().__init__(6024, "Token Mint in wrong order")

    code = 6024
    name = "InvalidTokenMintOrder"
    msg = "Token Mint in wrong order"


class RewardNotInitialized(ProgramError):
    def __init__(self) -> None:
        super().__init__(6025, "Reward not initialized")

    code = 6025
    name = "RewardNotInitialized"
    msg = "Reward not initialized"


class InvalidRewardIndex(ProgramError):
    def __init__(self) -> None:
        super().__init__(6026, "Invalid reward index")

    code = 6026
    name = "InvalidRewardIndex"
    msg = "Invalid reward index"


class RewardVaultAmountInsufficient(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6027,
            "Reward vault requires amount to support emissions for at least one day",
        )

    code = 6027
    name = "RewardVaultAmountInsufficient"
    msg = "Reward vault requires amount to support emissions for at least one day"


class FeeRateMaxExceeded(ProgramError):
    def __init__(self) -> None:
        super().__init__(6028, "Exceeded max fee rate")

    code = 6028
    name = "FeeRateMaxExceeded"
    msg = "Exceeded max fee rate"


class ProtocolFeeRateMaxExceeded(ProgramError):
    def __init__(self) -> None:
        super().__init__(6029, "Exceeded max protocol fee rate")

    code = 6029
    name = "ProtocolFeeRateMaxExceeded"
    msg = "Exceeded max protocol fee rate"


class MultiplicationShiftRightOverflow(ProgramError):
    def __init__(self) -> None:
        super().__init__(6030, "Multiplication with shift right overflow")

    code = 6030
    name = "MultiplicationShiftRightOverflow"
    msg = "Multiplication with shift right overflow"


class MulDivOverflow(ProgramError):
    def __init__(self) -> None:
        super().__init__(6031, "Muldiv overflow")

    code = 6031
    name = "MulDivOverflow"
    msg = "Muldiv overflow"


class MulDivInvalidInput(ProgramError):
    def __init__(self) -> None:
        super().__init__(6032, "Invalid div_u256 input")

    code = 6032
    name = "MulDivInvalidInput"
    msg = "Invalid div_u256 input"


class MultiplicationOverflow(ProgramError):
    def __init__(self) -> None:
        super().__init__(6033, "Multiplication overflow")

    code = 6033
    name = "MultiplicationOverflow"
    msg = "Multiplication overflow"


class InvalidSqrtPriceLimitDirection(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6034, "Provided SqrtPriceLimit not in the same direction as the swap."
        )

    code = 6034
    name = "InvalidSqrtPriceLimitDirection"
    msg = "Provided SqrtPriceLimit not in the same direction as the swap."


class ZeroTradableAmount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6035, "There are no tradable amount to swap.")

    code = 6035
    name = "ZeroTradableAmount"
    msg = "There are no tradable amount to swap."


class AmountOutBelowMinimum(ProgramError):
    def __init__(self) -> None:
        super().__init__(6036, "Amount out below minimum threshold")

    code = 6036
    name = "AmountOutBelowMinimum"
    msg = "Amount out below minimum threshold"


class AmountInAboveMaximum(ProgramError):
    def __init__(self) -> None:
        super().__init__(6037, "Amount in above maximum threshold")

    code = 6037
    name = "AmountInAboveMaximum"
    msg = "Amount in above maximum threshold"


class TickArraySequenceInvalidIndex(ProgramError):
    def __init__(self) -> None:
        super().__init__(6038, "Invalid index for tick array sequence")

    code = 6038
    name = "TickArraySequenceInvalidIndex"
    msg = "Invalid index for tick array sequence"


class AmountCalcOverflow(ProgramError):
    def __init__(self) -> None:
        super().__init__(6039, "Amount calculated overflows")

    code = 6039
    name = "AmountCalcOverflow"
    msg = "Amount calculated overflows"


class AmountRemainingOverflow(ProgramError):
    def __init__(self) -> None:
        super().__init__(6040, "Amount remaining overflows")

    code = 6040
    name = "AmountRemainingOverflow"
    msg = "Amount remaining overflows"


class InvalidIntermediaryMint(ProgramError):
    def __init__(self) -> None:
        super().__init__(6041, "Invalid intermediary mint")

    code = 6041
    name = "InvalidIntermediaryMint"
    msg = "Invalid intermediary mint"


class DuplicateTwoHopPool(ProgramError):
    def __init__(self) -> None:
        super().__init__(6042, "Duplicate two hop pool")

    code = 6042
    name = "DuplicateTwoHopPool"
    msg = "Duplicate two hop pool"


class InvalidBundleIndex(ProgramError):
    def __init__(self) -> None:
        super().__init__(6043, "Bundle index is out of bounds")

    code = 6043
    name = "InvalidBundleIndex"
    msg = "Bundle index is out of bounds"


class BundledPositionAlreadyOpened(ProgramError):
    def __init__(self) -> None:
        super().__init__(6044, "Position has already been opened")

    code = 6044
    name = "BundledPositionAlreadyOpened"
    msg = "Position has already been opened"


class BundledPositionAlreadyClosed(ProgramError):
    def __init__(self) -> None:
        super().__init__(6045, "Position has already been closed")

    code = 6045
    name = "BundledPositionAlreadyClosed"
    msg = "Position has already been closed"


class PositionBundleNotDeletable(ProgramError):
    def __init__(self) -> None:
        super().__init__(6046, "Unable to delete PositionBundle with open positions")

    code = 6046
    name = "PositionBundleNotDeletable"
    msg = "Unable to delete PositionBundle with open positions"


class UnsupportedTokenMint(ProgramError):
    def __init__(self) -> None:
        super().__init__(6047, "Token mint has unsupported attributes")

    code = 6047
    name = "UnsupportedTokenMint"
    msg = "Token mint has unsupported attributes"


class RemainingAccountsInvalidSlice(ProgramError):
    def __init__(self) -> None:
        super().__init__(6048, "Invalid remaining accounts")

    code = 6048
    name = "RemainingAccountsInvalidSlice"
    msg = "Invalid remaining accounts"


class RemainingAccountsInsufficient(ProgramError):
    def __init__(self) -> None:
        super().__init__(6049, "Insufficient remaining accounts")

    code = 6049
    name = "RemainingAccountsInsufficient"
    msg = "Insufficient remaining accounts"


class NoExtraAccountsForTransferHook(ProgramError):
    def __init__(self) -> None:
        super().__init__(6050, "Unable to call transfer hook without extra accounts")

    code = 6050
    name = "NoExtraAccountsForTransferHook"
    msg = "Unable to call transfer hook without extra accounts"


class IntermediateTokenAmountMismatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(6051, "Output and input amount mismatch")

    code = 6051
    name = "IntermediateTokenAmountMismatch"
    msg = "Output and input amount mismatch"


class TransferFeeCalculationError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6052, "Transfer fee calculation failed")

    code = 6052
    name = "TransferFeeCalculationError"
    msg = "Transfer fee calculation failed"


class RemainingAccountsDuplicatedAccountsType(ProgramError):
    def __init__(self) -> None:
        super().__init__(6053, "Same accounts type is provided more than once")

    code = 6053
    name = "RemainingAccountsDuplicatedAccountsType"
    msg = "Same accounts type is provided more than once"


class FullRangeOnlyPool(ProgramError):
    def __init__(self) -> None:
        super().__init__(6054, "This whirlpool only supports full-range positions")

    code = 6054
    name = "FullRangeOnlyPool"
    msg = "This whirlpool only supports full-range positions"


class TooManySupplementalTickArrays(ProgramError):
    def __init__(self) -> None:
        super().__init__(6055, "Too many supplemental tick arrays provided")

    code = 6055
    name = "TooManySupplementalTickArrays"
    msg = "Too many supplemental tick arrays provided"


class DifferentWhirlpoolTickArrayAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6056, "TickArray account for different whirlpool provided")

    code = 6056
    name = "DifferentWhirlpoolTickArrayAccount"
    msg = "TickArray account for different whirlpool provided"


class PartialFillError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6057, "Trade resulted in partial fill")

    code = 6057
    name = "PartialFillError"
    msg = "Trade resulted in partial fill"


CustomError = typing.Union[
    InvalidEnum,
    InvalidStartTick,
    TickArrayExistInPool,
    TickArrayIndexOutofBounds,
    InvalidTickSpacing,
    ClosePositionNotEmpty,
    DivideByZero,
    NumberCastError,
    NumberDownCastError,
    TickNotFound,
    InvalidTickIndex,
    SqrtPriceOutOfBounds,
    LiquidityZero,
    LiquidityTooHigh,
    LiquidityOverflow,
    LiquidityUnderflow,
    LiquidityNetError,
    TokenMaxExceeded,
    TokenMinSubceeded,
    MissingOrInvalidDelegate,
    InvalidPositionTokenAmount,
    InvalidTimestampConversion,
    InvalidTimestamp,
    InvalidTickArraySequence,
    InvalidTokenMintOrder,
    RewardNotInitialized,
    InvalidRewardIndex,
    RewardVaultAmountInsufficient,
    FeeRateMaxExceeded,
    ProtocolFeeRateMaxExceeded,
    MultiplicationShiftRightOverflow,
    MulDivOverflow,
    MulDivInvalidInput,
    MultiplicationOverflow,
    InvalidSqrtPriceLimitDirection,
    ZeroTradableAmount,
    AmountOutBelowMinimum,
    AmountInAboveMaximum,
    TickArraySequenceInvalidIndex,
    AmountCalcOverflow,
    AmountRemainingOverflow,
    InvalidIntermediaryMint,
    DuplicateTwoHopPool,
    InvalidBundleIndex,
    BundledPositionAlreadyOpened,
    BundledPositionAlreadyClosed,
    PositionBundleNotDeletable,
    UnsupportedTokenMint,
    RemainingAccountsInvalidSlice,
    RemainingAccountsInsufficient,
    NoExtraAccountsForTransferHook,
    IntermediateTokenAmountMismatch,
    TransferFeeCalculationError,
    RemainingAccountsDuplicatedAccountsType,
    FullRangeOnlyPool,
    TooManySupplementalTickArrays,
    DifferentWhirlpoolTickArrayAccount,
    PartialFillError,
]
CUSTOM_ERROR_MAP: dict[int, CustomError] = {
    6000: InvalidEnum(),
    6001: InvalidStartTick(),
    6002: TickArrayExistInPool(),
    6003: TickArrayIndexOutofBounds(),
    6004: InvalidTickSpacing(),
    6005: ClosePositionNotEmpty(),
    6006: DivideByZero(),
    6007: NumberCastError(),
    6008: NumberDownCastError(),
    6009: TickNotFound(),
    6010: InvalidTickIndex(),
    6011: SqrtPriceOutOfBounds(),
    6012: LiquidityZero(),
    6013: LiquidityTooHigh(),
    6014: LiquidityOverflow(),
    6015: LiquidityUnderflow(),
    6016: LiquidityNetError(),
    6017: TokenMaxExceeded(),
    6018: TokenMinSubceeded(),
    6019: MissingOrInvalidDelegate(),
    6020: InvalidPositionTokenAmount(),
    6021: InvalidTimestampConversion(),
    6022: InvalidTimestamp(),
    6023: InvalidTickArraySequence(),
    6024: InvalidTokenMintOrder(),
    6025: RewardNotInitialized(),
    6026: InvalidRewardIndex(),
    6027: RewardVaultAmountInsufficient(),
    6028: FeeRateMaxExceeded(),
    6029: ProtocolFeeRateMaxExceeded(),
    6030: MultiplicationShiftRightOverflow(),
    6031: MulDivOverflow(),
    6032: MulDivInvalidInput(),
    6033: MultiplicationOverflow(),
    6034: InvalidSqrtPriceLimitDirection(),
    6035: ZeroTradableAmount(),
    6036: AmountOutBelowMinimum(),
    6037: AmountInAboveMaximum(),
    6038: TickArraySequenceInvalidIndex(),
    6039: AmountCalcOverflow(),
    6040: AmountRemainingOverflow(),
    6041: InvalidIntermediaryMint(),
    6042: DuplicateTwoHopPool(),
    6043: InvalidBundleIndex(),
    6044: BundledPositionAlreadyOpened(),
    6045: BundledPositionAlreadyClosed(),
    6046: PositionBundleNotDeletable(),
    6047: UnsupportedTokenMint(),
    6048: RemainingAccountsInvalidSlice(),
    6049: RemainingAccountsInsufficient(),
    6050: NoExtraAccountsForTransferHook(),
    6051: IntermediateTokenAmountMismatch(),
    6052: TransferFeeCalculationError(),
    6053: RemainingAccountsDuplicatedAccountsType(),
    6054: FullRangeOnlyPool(),
    6055: TooManySupplementalTickArrays(),
    6056: DifferentWhirlpoolTickArrayAccount(),
    6057: PartialFillError(),
}


def from_code(code: int) -> typing.Optional[CustomError]:
    maybe_err = CUSTOM_ERROR_MAP.get(code)
    if maybe_err is None:
        return None
    return maybe_err
