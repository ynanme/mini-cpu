import unittest

from assembler import encode_r_type, encode_i_type, encode_memory_type, encode_branch_type, parse_instruction
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


class TestMemoryEncoding(unittest.TestCase):

    def test_load_word(self):
        encoded = encode_memory_type("lw", 1, 2, 8)

        expected = 0b01110_000001_000010_000000001000_000

        self.assertEqual(encoded, expected)

    def test_store_word_negative_offset(self):
        encoded = encode_memory_type("sw", 3, 5, -4)

        expected = 0b01111_000011_000101_111111111100_000

        self.assertEqual(encoded, expected)

    def test_invalid_offset(self):
        with self.assertRaises(ValueError):
            encode_memory_type("lw", 1, 2, 2048)

        with self.assertRaises(ValueError):
            encode_memory_type("sw", 1, 2, -2049)

    def test_invalid_operation(self):
        with self.assertRaises(ValueError):
            encode_memory_type("addi", 1, 2, 8)


class TestBranchEncoding(unittest.TestCase):

    def test_beq_encoding(self):
        encoded = encode_branch_type("beq", 1, 2, 5)

        expected = 0b10000_000001_000010_000000000101_000

        self.assertEqual(encoded, expected)

    def test_bgt_encoding(self):
        encoded = encode_branch_type("bgt", 3, 4, 100)

        expected = 0b10011_000011_000100_000001100100_000

        self.assertEqual(encoded, expected)

    def test_invalid_address(self):
        with self.assertRaises(ValueError):
            encode_branch_type("beq", 1, 2, -1)

        with self.assertRaises(ValueError):
            encode_branch_type("beq", 1, 2, 4096)

    def test_invalid_operation(self):
        with self.assertRaises(ValueError):
            encode_branch_type("addi", 1, 2, 5)


class TestInstructionParsing(unittest.TestCase):

    def test_register_instruction(self):
        result = parse_instruction("add $1, $2, $3")
        self.assertEqual(result, ("add", 1, 2, 3))

    def test_immediate_instruction(self):
        result = parse_instruction("subi $3, $4, -5")
        self.assertEqual(result, ("subi", 3, 4, -5))

    def test_memory_instruction(self):
        result = parse_instruction("lw $1, 8($2)")
        self.assertEqual(result, ("lw", 1, 2, 8))

    def test_memory_without_offset(self):
        result = parse_instruction("sw $3, ($0)")
        self.assertEqual(result, ("sw", 3, 0, 0))

    def test_branch_instruction(self):
        result = parse_instruction("beq $1, $2, end")
        self.assertEqual(result, ("beq", 1, 2, "end"))

    def test_comments(self):
        result = parse_instruction("add $1, $2, $3 # Addition")
        self.assertEqual(result, ("add", 1, 2, 3))

    def test_invalid_instruction(self):
        with self.assertRaises(ValueError):
            parse_instruction("unknown $1, $2, $3")

        with self.assertRaises(ValueError):
            parse_instruction("add $1, $2")


if __name__ == "__main__":
    unittest.main()
