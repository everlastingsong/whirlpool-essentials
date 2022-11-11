from ...errors import WhirlpoolError, MathErrorCode


class BitMath:
    @staticmethod
    def mul(n0: int, n1: int, limit: int) -> int:
        result = n0 * n1
        if BitMath.is_over_limit(result, limit):
            raise WhirlpoolError(MathErrorCode.MultiplicationOverflow)
        return result

    @staticmethod
    def mul_div(n0: int, n1: int, d: int, limit: int) -> int:
        return BitMath.mul_div_round_up_if(n0, n1, d, False, limit)

    @staticmethod
    def mul_div_round_up(n0: int, n1: int, d: int, limit: int) -> int:
        return BitMath.mul_div_round_up_if(n0, n1, d, True, limit)

    @staticmethod
    def mul_div_round_up_if(n0: int, n1: int, d: int, round_up: bool, limit: int) -> int:
        if d == 0:
            raise WhirlpoolError(MathErrorCode.DivideByZero)

        p = BitMath.mul(n0, n1, limit)
        n = p // d
        if round_up and p % d != 0:
            return n + 1
        else:
            return n

    @staticmethod
    def div_round_up(n: int, d: int) -> int:
        return BitMath.div_round_up_if(n, d, True)

    @staticmethod
    def div_round_up_if(n: int, d: int, round_up: bool) -> int:
        if d == 0:
            raise WhirlpoolError(MathErrorCode.DivideByZero)

        q = n // d
        if round_up and n % d != 0:
            return q + 1
        else:
            return q

    @staticmethod
    def is_over_limit(n0: int, limit: int) -> bool:
        ulimit_max = 2**limit - 1
        return n0 > ulimit_max
