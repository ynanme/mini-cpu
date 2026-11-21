import unittest

from emulator import CPU
from isa import REGISTER_COUNT, WORD_SIZE
from assembler import encode_r_type, encode_i_type, encode_memory_type, encode_branch_type, assemble_program


class TestCPUState(unittest.TestCase):

    def test_initial_state(self):
        cpu = CPU()

        self.assertEqual(len(cpu.registers), REGISTER_COUNT)
        self.assertTrue(all(value == 0 for value in cpu.registers))

        self.assertEqual(len(cpu.memory), 1024)
        self.assertTrue(all(value == 0 for value in cpu.memory))

        self.assertEqual(cpu.pc, 0)

    def test_zero_register_is_immutable(self):
        cpu = CPU()

        cpu.write_register(0, 42)

        self.assertEqual(cpu.registers[0], 0)

    def test_register_width(self):
        cpu = CPU()

        cpu.write_register(1, (1 << WORD_SIZE) + 5)

        self.assertEqual(cpu.registers[1], 5)

    def test_negative_register_value(self):
        cpu = CPU()

        cpu.write_register(1, -1)

        self.assertEqual(cpu.registers[1], (1 << WORD_SIZE) - 1)


class TestRegisterExecution(unittest.TestCase):

    def test_add(self):
        cpu = CPU()
        cpu.write_register(2, 10)
        cpu.write_register(3, 20)

        cpu.execute_instruction(encode_r_type("add", 1, 2, 3))

        self.assertEqual(cpu.registers[1], 30)

    def test_sub_overflow(self):
        cpu = CPU()
        cpu.write_register(2, 0)
        cpu.write_register(3, 1)

        cpu.execute_instruction(encode_r_type("sub", 1, 2, 3))

        self.assertEqual(cpu.registers[1], 0xFFFFFFFF)

    def test_mul_overflow(self):
        cpu = CPU()
        cpu.write_register(2, 0x80000000)
        cpu.write_register(3, 2)

        cpu.execute_instruction(encode_r_type("mul", 1, 2, 3))

        self.assertEqual(cpu.registers[1], 0)

    def test_signed_division(self):
        cpu = CPU()
        cpu.write_register(2, -7)
        cpu.write_register(3, 2)

        cpu.execute_instruction(encode_r_type("div", 1, 2, 3))

        self.assertEqual(cpu.registers[1], 0xFFFFFFFD)

    def test_division_by_zero(self):
        cpu = CPU()
        cpu.write_register(2, 10)

        with self.assertRaises(ZeroDivisionError):
            cpu.execute_instruction(encode_r_type("div", 1, 2, 3))

    def test_bitwise_operations(self):
        operations = {
            "and": 0b1000,
            "or":  0b1110,
            "xor": 0b0110,
        }

        for operation, expected in operations.items():
            with self.subTest(operation=operation):
                cpu = CPU()
                cpu.write_register(2, 0b1100)
                cpu.write_register(3, 0b1010)

                cpu.execute_instruction(
                    encode_r_type(operation, 1, 2, 3)
                )

                self.assertEqual(cpu.registers[1], expected)

    def test_zero_register(self):
        cpu = CPU()
        cpu.write_register(2, 10)
        cpu.write_register(3, 20)

        cpu.execute_instruction(encode_r_type("add", 0, 2, 3))

        self.assertEqual(cpu.registers[0], 0)


class TestImmediateExecution(unittest.TestCase):

    def test_addi_negative(self):
        cpu = CPU()
        cpu.write_register(2, 10)

        cpu.execute_instruction(encode_i_type("addi", 1, 2, -5))

        self.assertEqual(cpu.registers[1], 5)

    def test_subi_negative(self):
        cpu = CPU()
        cpu.write_register(2, 10)

        cpu.execute_instruction(encode_i_type("subi", 1, 2, -5))

        self.assertEqual(cpu.registers[1], 15)

    def test_muli_overflow(self):
        cpu = CPU()
        cpu.write_register(2, 0x80000000)

        cpu.execute_instruction(encode_i_type("muli", 1, 2, 2))

        self.assertEqual(cpu.registers[1], 0)

    def test_signed_divi(self):
        cpu = CPU()
        cpu.write_register(2, -7)

        cpu.execute_instruction(encode_i_type("divi", 1, 2, -2))

        self.assertEqual(cpu.registers[1], 3)

    def test_bitwise_immediates(self):
        cases = [
            ("andi", 0xFFFFFFFF, 4095, 4095),
            ("ori", 0x1000, 0xF00, 0x1F00),
            ("xori", 0b1100, 0b1010, 0b0110),
        ]

        for operation, value, immediate, expected in cases:
            with self.subTest(operation=operation):
                cpu = CPU()
                cpu.write_register(2, value)

                cpu.execute_instruction(
                    encode_i_type(operation, 1, 2, immediate)
                )

                self.assertEqual(cpu.registers[1], expected)

    def test_division_by_zero(self):
        cpu = CPU()
        cpu.write_register(2, 10)

        with self.assertRaises(ZeroDivisionError):
            cpu.execute_instruction(encode_i_type("divi", 1, 2, 0))

    def test_zero_register(self):
        cpu = CPU()
        cpu.write_register(2, 10)

        cpu.execute_instruction(encode_i_type("addi", 0, 2, 5))

        self.assertEqual(cpu.registers[0], 0)


class TestMemoryExecution(unittest.TestCase):

    def test_load_word(self):
        cpu = CPU()
        cpu.write_register(2, 10)
        cpu.memory[18] = 42

        cpu.execute_instruction(
            encode_memory_type("lw", 1, 2, 8)
        )

        self.assertEqual(cpu.registers[1], 42)

    def test_store_word(self):
        cpu = CPU()
        cpu.write_register(1, 42)
        cpu.write_register(2, 10)

        cpu.execute_instruction(
            encode_memory_type("sw", 1, 2, 8)
        )

        self.assertEqual(cpu.memory[18], 42)

    def test_negative_offset(self):
        cpu = CPU()
        cpu.write_register(1, 99)
        cpu.write_register(2, 10)

        cpu.execute_instruction(
            encode_memory_type("sw", 1, 2, -4)
        )

        cpu.execute_instruction(
            encode_memory_type("lw", 3, 2, -4)
        )

        self.assertEqual(cpu.memory[6], 99)
        self.assertEqual(cpu.registers[3], 99)

    def test_invalid_address(self):
        cpu = CPU()

        with self.assertRaises(IndexError):
            cpu.execute_instruction(
                encode_memory_type("lw", 1, 0, -1)
            )

        with self.assertRaises(IndexError):
            cpu.execute_instruction(
                encode_memory_type("sw", 1, 0, 1024)
            )

    def test_zero_register(self):
        cpu = CPU()
        cpu.memory[5] = 42

        cpu.execute_instruction(
            encode_memory_type("lw", 0, 0, 5)
        )

        self.assertEqual(cpu.registers[0], 0)


class TestBranchExecution(unittest.TestCase):

    def test_beq_taken(self):
        cpu = CPU()
        cpu.write_register(1, 42)
        cpu.write_register(2, 42)

        target = cpu.execute_instruction(
            encode_branch_type("beq", 1, 2, 5)
        )

        self.assertEqual(target, 5)

    def test_beq_not_taken(self):
        cpu = CPU()
        cpu.write_register(1, 10)
        cpu.write_register(2, 20)

        target = cpu.execute_instruction(
            encode_branch_type("beq", 1, 2, 5)
        )

        self.assertIsNone(target)

    def test_bne(self):
        cpu = CPU()
        cpu.write_register(1, 10)
        cpu.write_register(2, 20)

        target = cpu.execute_instruction(
            encode_branch_type("bne", 1, 2, 0)
        )

        self.assertEqual(target, 0)

    def test_blo_unsigned(self):
        cpu = CPU()
        cpu.write_register(1, 1)
        cpu.write_register(2, -1)

        target = cpu.execute_instruction(
            encode_branch_type("blo", 1, 2, 8)
        )

        self.assertEqual(target, 8)

    def test_bgt_signed(self):
        cpu = CPU()
        cpu.write_register(1, -1)
        cpu.write_register(2, -2)

        target = cpu.execute_instruction(
            encode_branch_type("bgt", 1, 2, 10)
        )

        self.assertEqual(target, 10)

    def test_pc_unchanged(self):
        cpu = CPU()
        cpu.write_register(1, 42)
        cpu.write_register(2, 42)

        cpu.execute_instruction(
            encode_branch_type("beq", 1, 2, 5)
        )

        self.assertEqual(cpu.pc, 0)


class TestProgramStepping(unittest.TestCase):

    def test_load_program(self):
        cpu = CPU()
        program = [
            encode_i_type("addi", 1, 0, 10),
            encode_i_type("addi", 2, 0, 20),
        ]

        cpu.load_program(program)

        self.assertEqual(cpu.program, program)
        self.assertEqual(cpu.pc, 0)

    def test_sequential_execution(self):
        cpu = CPU()
        cpu.load_program([
            encode_i_type("addi", 1, 0, 10),
            encode_i_type("addi", 2, 1, 20),
        ])

        self.assertTrue(cpu.step())
        self.assertEqual(cpu.registers[1], 10)
        self.assertEqual(cpu.pc, 1)

        self.assertTrue(cpu.step())
        self.assertEqual(cpu.registers[2], 30)
        self.assertEqual(cpu.pc, 2)

        self.assertFalse(cpu.step())

    def test_backward_branch(self):
        cpu = CPU()

        source = """
            addi $1, $0, 2

        loop:
            subi $1, $1, 1
            bne $1, $0, loop
        """

        cpu.load_program(assemble_program(source))

        cpu.step()  # r1 = 2, PC = 1
        cpu.step()  # r1 = 1, PC = 2
        cpu.step()  # Branch taken, PC = 1

        self.assertEqual(cpu.pc, 1)
        self.assertEqual(cpu.registers[1], 1)

        cpu.step()  # r1 = 0, PC = 2
        cpu.step()  # Branch not taken, PC = 3

        self.assertEqual(cpu.pc, 3)
        self.assertFalse(cpu.step())

    def test_branch_to_program_end(self):
        cpu = CPU()

        cpu.load_program([
            encode_branch_type("beq", 0, 0, 2),
            encode_i_type("addi", 1, 0, 42),
        ])

        self.assertTrue(cpu.step())

        self.assertEqual(cpu.pc, 2)
        self.assertEqual(cpu.registers[1], 0)
        self.assertFalse(cpu.step())

    def test_invalid_branch_target(self):
        cpu = CPU()

        cpu.load_program([
            encode_branch_type("beq", 0, 0, 100),
        ])

        with self.assertRaises(IndexError):
            cpu.step()

        self.assertEqual(cpu.pc, 0)

    def test_empty_program(self):
        cpu = CPU()
        cpu.load_program([])

        self.assertFalse(cpu.step())
        self.assertEqual(cpu.pc, 0)


if __name__ == "__main__":
    unittest.main()
