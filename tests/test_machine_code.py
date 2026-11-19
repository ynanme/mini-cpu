import unittest
import tempfile

from pathlib import Path

from machine_code import write_machine_code, read_machine_code


class TestMachineCode(unittest.TestCase):

    def test_write_machine_code(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.bin"

            write_machine_code(path, [0x38200028])

            self.assertEqual(
                path.read_bytes(),
                b"\x38\x20\x00\x28",
            )

    def test_read_machine_code(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.bin"

            path.write_bytes(b"\x38\x20\x00\x28")

            self.assertEqual(
                read_machine_code(path),
                [0x38200028],
            )

    def test_invalid_instruction_size(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.bin"

            path.write_bytes(b"\x38\x20\x00")

            with self.assertRaises(ValueError):
                read_machine_code(path)

    def test_invalid_instruction_value(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.bin"

            with self.assertRaises(ValueError):
                write_machine_code(path, [1 << 32])


if __name__ == "__main__":
    unittest.main()
