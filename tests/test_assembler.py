import unittest

from assembler import encode_r_type, encode_i_type
from isa import IMMEDIATE_SHIFT, IMMEDIATE_MASK


class TestRegisterEncoding(unittest.TestCase):

    def test_add_encoding(self):
        encoded = encode_r_type("add", 1, 2, 3)

        expected = 0b00000_000001_000010_000011_000000000

        self.assertEqual(encoded, expected)

    def test_xor_encoding(self):
        encoded = encode_r_type("xor", 5, 10, 20)

        expected = 0b00110_000101_001010_010100_000000000

        self.assertEqual(encoded, expected)

    def test_invalid_register(self):
        with self.assertRaises(ValueError):
            encode_r_type("add", 64, 2, 3)

    def test_invalid_operation(self):
        with self.assertRaises(ValueError):
            encode_r_type("addi", 1, 2, 3)


class TestImmediateEncoding(unittest.TestCase):

    def test_positive_immediate(self):
        encoded = encode_i_type("addi", 1, 2, 42)

        immediate = (encoded >> IMMEDIATE_SHIFT) & IMMEDIATE_MASK

        self.assertEqual(immediate, 42)

    def test_negative_immediate(self):
        encoded = encode_i_type("subi", 3, 4, -5)

        immediate = (encoded >> IMMEDIATE_SHIFT) & IMMEDIATE_MASK

        self.assertEqual(immediate, 0b111111111011)

    def test_unsigned_immediate(self):
        encoded = encode_i_type("andi", 1, 2, 4095)

        immediate = (encoded >> IMMEDIATE_SHIFT) & IMMEDIATE_MASK

        self.assertEqual(immediate, 4095)

    def test_out_of_range_immediate(self):
        with self.assertRaises(ValueError):
            encode_i_type("addi", 1, 2, 2048)

        with self.assertRaises(ValueError):
            encode_i_type("andi", 1, 2, -1)

    def test_invalid_register(self):
        with self.assertRaises(ValueError):
            encode_i_type("addi", 64, 2, 10)


if __name__ == "__main__":
    unittest.main()
