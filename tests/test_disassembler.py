import unittest

from assembler import (
    assemble_program,
    encode_r_type,
    encode_i_type,
    encode_memory_type,
    encode_branch_type,
)
from disassembler import (
    disassemble_instruction,
    disassemble_program,
)


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


class TestProgramDisassembly(unittest.TestCase):

    def test_program_without_branches(self):
        source = """
            addi $1, $0, 5
            addi $2, $1, 10
        """

        program = assemble_program(source)

        self.assertEqual(
            disassemble_program(program),
            "    addi $1, $0, 5\n"
            "    addi $2, $1, 10",
        )

    def test_backward_branch(self):
        source = """
            addi $1, $0, 3

        loop:
            subi $1, $1, 1
            bne $1, $0, loop
        """

        program = assemble_program(source)

        self.assertEqual(
            disassemble_program(program),
            "    addi $1, $0, 3\n"
            "label_1:\n"
            "    subi $1, $1, 1\n"
            "    bne $1, $0, label_1",
        )

    def test_shared_branch_target(self):
        source = """
            beq $1, $2, done
            bne $3, $0, done

        done:
            addi $4, $0, 42
        """

        program = assemble_program(source)
        assembly = disassemble_program(program)

        self.assertEqual(assembly.count("label_2:"), 1)
        self.assertEqual(assembly.count("label_2"), 3)

    def test_branch_to_program_end(self):
        source = """
            beq $0, $0, end
            addi $1, $0, 42

        end:
        """

        program = assemble_program(source)

        self.assertEqual(
            disassemble_program(program),
            "    beq $0, $0, label_2\n"
            "    addi $1, $0, 42\n"
            "label_2:",
        )

    def test_out_of_range_branch_target(self):
        program = assemble_program("beq $0, $0, 100")

        self.assertEqual(
            disassemble_program(program),
            "    beq $0, $0, 100",
        )

    def test_program_round_trip(self):
        source = """
            addi $1, $0, 5

        loop:
            subi $1, $1, 1
            bne $1, $0, loop
            sw $1, 10($0)
        """

        original = assemble_program(source)
        assembly = disassemble_program(original)
        reconstructed = assemble_program(assembly)

        self.assertEqual(reconstructed, original)


if __name__ == "__main__":
    unittest.main()
