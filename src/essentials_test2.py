import unittest
from decimal import Decimal
from solana.publickey import PublicKey

from .whirlpool_essentials import Q64FixedPointMath, DecimalUtil
from .whirlpool_essentials.types import Percentage
from .whirlpool_essentials.invariant import InvaliantFailedError


class PercentageTestCase(unittest.TestCase):
    def test_from_fraction_01(self):
        result = Percentage.from_fraction(1, 100)  # 1%
        self.assertEqual(1, result.numerator)
        self.assertEqual(100, result.denominator)

    def test_from_fraction_02(self):
        result = Percentage.from_fraction(3, 1000)  # 0.3%
        self.assertEqual(3, result.numerator)
        self.assertEqual(1000, result.denominator)

    def test_from_fraction_03(self):
        result = Percentage.from_fraction(5, 10000)  # 0.05%
        self.assertEqual(5, result.numerator)
        self.assertEqual(10000, result.denominator)

    def test_from_fraction_04(self):
        result = Percentage.from_fraction(0, 100)  # 0%
        self.assertEqual(0, result.numerator)
        self.assertEqual(100, result.denominator)

    def test_from_fraction_05(self):
        result = Percentage.from_fraction(100, 100)  # 100%
        self.assertEqual(100, result.numerator)
        self.assertEqual(100, result.denominator)

    def test_to_decimal_01(self):
        result = Percentage.from_fraction(1, 100).to_decimal()
        self.assertEqual(Decimal("0.01"), result)

    def test_to_decimal_02(self):
        result = Percentage.from_fraction(5, 10000).to_decimal()
        self.assertEqual(Decimal("0.0005"), result)

    def test_adjust_add_01(self):
        percentage = Percentage.from_fraction(1, 100)
        result = percentage.adjust_add(10000)
        self.assertEqual(10100, result)

    def test_adjust_add_02(self):
        percentage = Percentage.from_fraction(1, 1000)
        result = percentage.adjust_add(10000)
        self.assertEqual(10010, result)

    def test_adjust_add_03(self):
        percentage = Percentage.from_fraction(1, 1000)
        result = percentage.adjust_add(10001)
        self.assertEqual(10001+10, result)

    def test_adjust_add_04(self):
        percentage = Percentage.from_fraction(1, 1000)
        result = percentage.adjust_add(10999)
        self.assertEqual(10999+10, result)

    def test_adjust_add_05(self):
        percentage = Percentage.from_fraction(1, 1000)
        result = percentage.adjust_add(11000)
        self.assertEqual(11000+11, result)

    def test_adjust_sub_01(self):
        percentage = Percentage.from_fraction(1, 100)
        result = percentage.adjust_sub(10000)
        self.assertEqual(9900, result)

    def test_adjust_sub_02(self):
        percentage = Percentage.from_fraction(1, 1000)
        result = percentage.adjust_sub(10000)
        self.assertEqual(9990, result)

    def test_adjust_sub_03(self):
        percentage = Percentage.from_fraction(1, 1000)
        result = percentage.adjust_sub(10001)
        self.assertEqual(9990, result)

    def test_str_01(self):
        percentage = Percentage.from_fraction(1, 1000)
        result = str(percentage)
        self.assertEqual("1/1000", result)

    def test_str_02(self):
        percentage = Percentage.from_fraction(5, 10000)
        result = str(percentage)
        self.assertEqual("5/10000", result)

    def test_str_03(self):
        percentage = Percentage.from_percentage("1")
        result = str(percentage)
        self.assertEqual("1/100", result)

    def test_from_percentage_01(self):
        result = Percentage.from_percentage("1")  # 1%
        self.assertEqual(1, result.numerator)
        self.assertEqual(100, result.denominator)

    def test_from_percentage_02(self):
        result = Percentage.from_percentage("0.3")  # 0.3%
        self.assertEqual(3, result.numerator)
        self.assertEqual(1000, result.denominator)

    def test_from_percentage_03(self):
        result = Percentage.from_percentage("0.05")  # 0.05%
        self.assertEqual(1, result.numerator)
        self.assertEqual(2000, result.denominator)

    def test_from_percentage_04(self):
        result = Percentage.from_percentage("0")  # 0%
        self.assertEqual(0, result.numerator)
        self.assertEqual(1, result.denominator)

    def test_from_percentage_05(self):
        result = Percentage.from_percentage("0.0001")  # 0.0001%
        self.assertEqual(1, result.numerator)
        self.assertEqual(1000000, result.denominator)

    def test_from_percentage_06(self):
        result = Percentage.from_percentage("100")  # 100%
        self.assertEqual(1, result.numerator)
        self.assertEqual(1, result.denominator)

    def test_from_percentage_07(self):
        result = Percentage.from_percentage("0.0001999")  # 0.0001999%
        self.assertEqual(1, result.numerator)
        self.assertEqual(1000000, result.denominator)

    def test_from_percentage_08(self):
        try:
            Percentage.from_percentage("100.1")  # greater than 100%
            self.fail()
        except InvaliantFailedError:
            pass

    def test_from_percentage_09(self):
        try:
            Percentage.from_percentage("0.000099999")  # less than 0.0001 %
            self.fail()
        except InvaliantFailedError:
            pass


class Q64FixedPointMathTestCase(unittest.TestCase):
    def test_int_to_x64int_01(self):
        result = Q64FixedPointMath.int_to_x64int(1)
        expect = 1 << 64
        self.assertEqual(expect, result)

    def test_int_to_x64int_02(self):
        result = Q64FixedPointMath.int_to_x64int(100)
        expect = 100 << 64
        self.assertEqual(expect, result)

    def test_x64int_to_int_01(self):
        result = Q64FixedPointMath.x64int_to_decimal(1 << 64)
        expect = 1
        self.assertEqual(expect, result)

    def test_x64int_to_int_02(self):
        result = Q64FixedPointMath.x64int_to_decimal(100 << 64)
        expect = 100
        self.assertEqual(expect, result)

    def test_decimal_to_x64int_01(self):
        result = Q64FixedPointMath.decimal_to_x64int(Decimal(1))
        expect = 1 << 64
        self.assertEqual(expect, result)

    def test_decimal_to_x64int_02(self):
        result = Q64FixedPointMath.decimal_to_x64int(Decimal(100))
        expect = 100 << 64
        self.assertEqual(expect, result)

    def test_decimal_to_x64int_03(self):
        result = Q64FixedPointMath.decimal_to_x64int(Decimal("1.75"))
        expect = (4+2+1) << 62
        self.assertEqual(expect, result)

    def test_decimal_to_x64int_04(self):
        result = Q64FixedPointMath.decimal_to_x64int(Decimal("0.125"))
        expect = (0+0+0+1) << 61
        self.assertEqual(expect, result)

    def test_x64int_to_decimal_01(self):
        result = Q64FixedPointMath.x64int_to_decimal(1 << 64)
        expect = Decimal(1)
        self.assertEqual(expect, result)

    def test_x64int_to_decimal_02(self):
        result = Q64FixedPointMath.x64int_to_decimal(100 << 64)
        expect = Decimal(100)
        self.assertEqual(expect, result)

    def test_x64int_to_decimal_03(self):
        result = Q64FixedPointMath.x64int_to_decimal((4+2+1) << 62)
        expect = Decimal("1.75")
        self.assertEqual(expect, result)

    def test_x64int_to_decimal_04(self):
        result = Q64FixedPointMath.x64int_to_decimal((0+0+0+1) << 61)
        expect = Decimal("0.125")
        self.assertEqual(expect, result)


class DecimalUtilTestCase(unittest.TestCase):
    def test_to_u64_01(self):
        result = DecimalUtil.to_u64(Decimal(500), 0)
        self.assertEqual(500, result)

    def test_to_u64_02(self):
        result = DecimalUtil.to_u64(Decimal(500))
        self.assertEqual(500, result)

    def test_to_u64_03(self):
        result = DecimalUtil.to_u64(Decimal(500), 9)
        self.assertEqual(500*10**9, result)

    def test_to_u64_04(self):
        result = DecimalUtil.to_u64(Decimal("0.5"), 6)
        self.assertEqual(500000, result)

    def test_to_u64_05(self):
        result = DecimalUtil.to_u64(Decimal("0.000001"), 6)
        self.assertEqual(1, result)

    def test_to_u64_06(self):
        result = DecimalUtil.to_u64(Decimal(0), 9)
        self.assertEqual(0, result)

    def test_to_u64_07(self):
        result = DecimalUtil.to_u64(Decimal("0.000000001"), 6)
        self.assertEqual(0, result)

    def test_from_u64_01(self):
        result = DecimalUtil.from_u64(500, 0)
        self.assertEqual(Decimal(500), result)

    def test_from_u64_02(self):
        result = DecimalUtil.from_u64(500)
        self.assertEqual(Decimal(500), result)

    def test_from_u64_03(self):
        result = DecimalUtil.from_u64(500*10**9, 9)
        self.assertEqual(Decimal(500), result)

    def test_from_u64_04(self):
        result = DecimalUtil.from_u64(500000, 6)
        self.assertEqual(Decimal("0.5"), result)

    def test_from_u64_05(self):
        result = DecimalUtil.from_u64(1, 6)
        self.assertEqual(Decimal("0.000001"), result)

    def test_from_u64_06(self):
        result = DecimalUtil.from_u64(0, 9)
        self.assertEqual(Decimal(0), result)


if __name__ == "__main__":
    unittest.main()