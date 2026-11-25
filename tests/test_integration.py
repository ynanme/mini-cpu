import tempfile
import unittest
from pathlib import Path

from assembler import assemble_program
from decoder import decode_instruction
from disassembler import disassemble_program
from emulator import CPU
from isa import OPCODES, WORD_MASK
from machine_code import read_machine_code, write_machine_code


EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


class TestTemperatureMonitor(unittest.TestCase):

    def test_initializes_temperature_samples(self):
        source = (
            EXAMPLES_DIR / "temperature_monitor.asm"
        ).read_text(encoding="utf-8")

        cpu = CPU()
        cpu.load_program(assemble_program(source))
        cpu.run()

        temperatures = [-4, 12, 18, 45, 7, 39, -3, 20]

        expected = [
            value & WORD_MASK
            for value in temperatures
        ]

        self.assertEqual(cpu.memory[100:108], expected)

        # Check that adjacent memory locations are untouched.
        self.assertEqual(cpu.memory[99], 0)
        self.assertEqual(cpu.memory[108], 0)

    def test_temperature_sum(self):
        source = (
            EXAMPLES_DIR / "temperature_monitor.asm"
        ).read_text(encoding="utf-8")

        cpu = CPU()
        cpu.load_program(assemble_program(source))
        cpu.run()

        self.assertEqual(cpu.memory[200], 134)
        self.assertEqual(cpu.registers[5], 134)

        # All eight samples have been processed.
        self.assertEqual(cpu.registers[4], 8)

        # The pointer now references the next memory location.
        self.assertEqual(cpu.registers[3], 108)
    
    def test_temperature_extrema(self):
        source = (
            EXAMPLES_DIR / "temperature_monitor.asm"
        ).read_text(encoding="utf-8")

        cpu = CPU()
        cpu.load_program(assemble_program(source))
        cpu.run()

        # Check minimum temperature.
        self.assertEqual(cpu.registers[8], -4 & WORD_MASK)
        self.assertEqual(cpu.memory[202], -4 & WORD_MASK)

        # Check maximum temperature.
        self.assertEqual(cpu.registers[9], 45)
        self.assertEqual(cpu.memory[203], 45)

        # Check index of the maximum temperature.
        self.assertEqual(cpu.registers[10], 3)
        self.assertEqual(cpu.memory[206], 3)
    
    def test_average_and_alerts(self):
        source = (
            EXAMPLES_DIR / "temperature_monitor.asm"
        ).read_text(encoding="utf-8")

        cpu = CPU()
        cpu.load_program(assemble_program(source))
        cpu.run()

        # Average temperature
        self.assertEqual(cpu.registers[13], 16)
        self.assertEqual(cpu.memory[201], 16)

        # Samples strictly above 30°C
        self.assertEqual(cpu.registers[12], 2)
        self.assertEqual(cpu.memory[204], 2)

        # Bit 0: overheating, bit 1: negative temperature
        self.assertEqual(cpu.registers[15], 0b11)
        self.assertEqual(cpu.memory[205], 0b11)

    def test_threshold_boundaries(self):
        source = (
            EXAMPLES_DIR / "temperature_monitor.asm"
        ).read_text(encoding="utf-8")

        cpu = CPU()
        cpu.load_program(assemble_program(source))

        # Execute the 17 data-initialization instructions.
        for _ in range(17):
            cpu.step()

        # Replace critical values with boundary values.
        cpu.memory[100] = 0
        cpu.memory[103] = 30
        cpu.memory[105] = 30
        cpu.memory[106] = 0

        # Resume execution with the modified samples.
        cpu.run()

        self.assertEqual(cpu.memory[204], 0)
        self.assertEqual(cpu.memory[205], 0)
        self.assertEqual(cpu.memory[201], 14)
    
    def run_with_samples(self, samples: list[int]) -> CPU:
        """Run the monitor with a custom set of temperature samples."""

        self.assertEqual(len(samples), 8)

        source = (
            EXAMPLES_DIR / "temperature_monitor.asm"
        ).read_text(encoding="utf-8")

        cpu = CPU()
        cpu.load_program(assemble_program(source))

        # Execute the 17 sample-initialization instructions.
        for _ in range(17):
            cpu.step()

        # Replace the initialized samples before processing.
        for index, temperature in enumerate(samples):
            cpu.memory[100 + index] = temperature & WORD_MASK

        cpu.run()

        return cpu
    
    def test_monitor_scenarios(self):
        cases = [
            (
                "no_alerts",
                [0, 10, 20, 30, 5, 15, 29, 0],
                [109, 13, 0, 30, 0, 0, 3],
            ),
            (
                "overheating_only",
                [10, 20, 31, 30, 0, 40, 20, 10],
                [161, 20, 0, 40, 2, 1, 5],
            ),
            (
                "negative_only",
                [0, -4, 10, 20, -1, 30, 5, 0],
                [60, 7, -4, 30, 0, 2, 5],
            ),
            (
                "both_alerts",
                [-4, 12, 18, 45, 7, 39, -3, 20],
                [134, 16, -4, 45, 2, 3, 3],
            ),
            (
                "repeated_maximum",
                [5, 40, 40, 10, 0, -1, 8, 3],
                [105, 13, -1, 40, 2, 3, 1],
            ),
            (
                "all_negative",
                [-9, -8, -7, -6, -5, -4, -3, -2],
                [-44, -5, -9, -2, 0, 2, 7],
            ),
        ]

        for name, samples, expected in cases:
            with self.subTest(scenario=name):
                cpu = self.run_with_samples(samples)

                expected_words = [
                    value & WORD_MASK for value in expected
                ]

                self.assertEqual(
                    cpu.memory[200:207],
                    expected_words,
                )

                self.assertEqual(cpu.pc, len(cpu.program))

    def test_versioned_program_consistency(self):
        source = (
            EXAMPLES_DIR / "temperature_monitor.asm"
        ).read_text(encoding="utf-8")

        disassembled = (
            EXAMPLES_DIR / "temperature_monitor.dis.asm"
        ).read_text(encoding="utf-8")

        binary = read_machine_code(
            EXAMPLES_DIR / "temperature_monitor.bin"
        )

        # Source assembly must match the versioned binary.
        self.assertEqual(
            assemble_program(source),
            binary,
        )

        # Disassembled assembly must reconstruct the same binary.
        self.assertEqual(
            assemble_program(disassembled),
            binary,
        )

        # The versioned disassembly must match the current output.
        self.assertEqual(
            disassembled.rstrip("\n"),
            disassemble_program(binary),
        )


class TestFullISAIntegration(unittest.TestCase):

    def test_all_instructions(self):
        source = """
            # Initialize operands
            addi $1, $0, 12
            addi $2, $0, 5

            # Register arithmetic and logic
            add $3, $1, $2
            sub $4, $1, $2
            mul $5, $1, $2
            div $6, $1, $2
            and $7, $1, $2
            or $8, $1, $2
            xor $9, $1, $2

            # Immediate arithmetic and logic
            subi $10, $1, 2
            muli $11, $2, 3
            divi $12, $1, 4
            andi $13, $1, 10
            ori $14, $2, 8
            xori $15, $1, 3

            # Memory operations
            sw $3, 220($0)
            lw $16, 220($0)

            # Conditional branches
            beq $1, $1, equal
            addi $20, $0, 1

        equal:
            bne $1, $2, different
            addi $21, $0, 1

        different:
            blo $2, $1, lower
            addi $22, $0, 1

        lower:
            bgt $1, $2, greater
            addi $23, $0, 1

        greater:
        """

        # Assemble the complete program.
        program = assemble_program(source)

        # Every ISA operation must appear in the program.
        operations = {
            decode_instruction(instruction)[0]
            for instruction in program
        }

        self.assertEqual(operations, set(OPCODES))

        # Serialize and reload the machine code.
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "isa_test.bin"

            write_machine_code(binary, program)
            loaded = read_machine_code(binary)

        self.assertEqual(loaded, program)

        # Disassembly must preserve the machine code.
        disassembled = disassemble_program(loaded)

        self.assertEqual(
            assemble_program(disassembled),
            loaded,
        )

        # Execute the program.
        cpu = CPU()
        cpu.load_program(loaded)

        steps = cpu.run()

        # Verify arithmetic and logical results.
        expected_registers = {
            1: 12,
            2: 5,
            3: 17,
            4: 7,
            5: 60,
            6: 2,
            7: 4,
            8: 13,
            9: 9,
            10: 10,
            11: 15,
            12: 3,
            13: 8,
            14: 13,
            15: 15,
            16: 17,
        }

        for register, expected in expected_registers.items():
            with self.subTest(register=register):
                self.assertEqual(
                    cpu.registers[register],
                    expected,
                )

        # Verify memory operations.
        self.assertEqual(cpu.memory[220], 17)

        # Branches must skip these instructions.
        for register in range(20, 24):
            self.assertEqual(cpu.registers[register], 0)

        # Verify normal program termination.
        self.assertEqual(steps, 21)
        self.assertEqual(cpu.pc, len(program))
        

if __name__ == "__main__":
    unittest.main()
