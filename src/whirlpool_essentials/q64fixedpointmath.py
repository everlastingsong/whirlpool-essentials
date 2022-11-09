import math
from decimal import Decimal


class Q64FixedPointMath:
    @staticmethod
    def int_to_x64int(num: int) -> int:
        return num * 2**64

    @staticmethod
    def x64int_to_int(num: int) -> int:
        return num // 2**64

    @staticmethod
    def x64int_to_decimal(num: int) -> Decimal:
        shift_64 = Decimal(2)**64
        return Decimal(num) / shift_64

    @staticmethod
    def decimal_to_x64int(num: Decimal) -> int:
        shift_64 = Decimal(2)**64
        return math.floor(num * shift_64)
