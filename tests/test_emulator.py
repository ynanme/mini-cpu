import unittest

from emulator import CPU
from isa import REGISTER_COUNT, WORD_SIZE


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


if __name__ == "__main__":
    unittest.main()
