import unittest

from decoder import decode_instruction


class TestInstructionDecoding(unittest.TestCase):

    def test_r_type(self):
        instruction = 0b00110_000101_001010_010100_000000000

        self.assertEqual(
            decode_instruction(instruction),
            ("xor", 5, 10, 20),
        )

    def test_signed_immediate(self):
        instruction = 0b01000_000011_000100_111111111011_000

        self.assertEqual(
            decode_instruction(instruction),
            ("subi", 3, 4, -5),
        )

    def test_unsigned_immediate(self):
        instruction = 0b01011_000001_000010_111111111111_000

        self.assertEqual(
            decode_instruction(instruction),
            ("andi", 1, 2, 4095),
        )

    def test_memory_offset(self):
        instruction = 0b01111_000011_000101_111111111100_000

        self.assertEqual(
            decode_instruction(instruction),
            ("sw", 3, 5, -4),
        )

    def test_branch_address(self):
        instruction = 0b10000_000001_000010_000000000101_000

        self.assertEqual(
            decode_instruction(instruction),
            ("beq", 1, 2, 5),
        )

    def test_unknown_opcode(self):
        instruction = 31 << 27

        with self.assertRaises(ValueError):
            decode_instruction(instruction)

    def test_invalid_instruction_width(self):
        with self.assertRaises(ValueError):
            decode_instruction(1 << 32)

        with self.assertRaises(ValueError):
            decode_instruction(-1)

    def test_reserved_bits(self):
        instruction = 0b00000_000001_000010_000011_000000001

        with self.assertRaises(ValueError):
            decode_instruction(instruction)


if __name__ == "__main__":
    unittest.main()
