import unittest

from assembler import (
    assemble_program,
    encode_r_type,
    encode_i_type,
    encode_memory_type,
    encode_branch_type,
)
from disassembler import disassemble_instruction


class TestInstructionDisassembly(unittest.TestCase):

    def test_r_type(self):
        instruction = encode_r_type("xor", 5, 10, 20)

        self.assertEqual(
            disassemble_instruction(instruction),
            "xor $5, $10, $20",
        )

    def test_signed_immediate(self):
        instruction = encode_i_type("subi", 3, 4, -5)

        self.assertEqual(
            disassemble_instruction(instruction),
            "subi $3, $4, -5",
        )

    def test_unsigned_immediate(self):
        instruction = encode_i_type("andi", 1, 2, 4095)

        self.assertEqual(
            disassemble_instruction(instruction),
            "andi $1, $2, 4095",
        )

    def test_memory_instruction(self):
        instruction = encode_memory_type("lw", 1, 2, -8)

        self.assertEqual(
            disassemble_instruction(instruction),
            "lw $1, -8($2)",
        )

    def test_branch_instruction(self):
        instruction = encode_branch_type("beq", 1, 2, 5)

        self.assertEqual(
            disassemble_instruction(instruction),
            "beq $1, $2, 5",
        )

    def test_round_trip(self):
        instruction = encode_i_type("addi", 1, 2, -42)

        assembly = disassemble_instruction(instruction)
        reassembled = assemble_program(assembly)

        self.assertEqual(reassembled, [instruction])


if __name__ == "__main__":
    unittest.main()
