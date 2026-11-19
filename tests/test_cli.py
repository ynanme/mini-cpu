import unittest
import tempfile

from pathlib import Path

from mcpu import main
from machine_code import read_machine_code
from assembler import assemble_program


class TestCLI(unittest.TestCase):

    def test_assemble_default_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "program.asm"
            source.write_text("addi $1, $0, 5\n")

            main(["assemble", str(source)])

            output = source.with_suffix(".bin")

            self.assertTrue(output.exists())

            expected = assemble_program(source.read_text())
            self.assertEqual(read_machine_code(output), expected)

    def test_assemble_custom_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "program.asm"
            output = Path(directory) / "custom.bin"

            source.write_text("add $1, $2, $3\n")

            main(["assemble", str(source), "-o", str(output)])

            self.assertTrue(output.exists())

    def test_prevent_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "program.asm"
            output = source.with_suffix(".bin")

            source.write_text("addi $1, $0, 5\n")
            output.write_bytes(b"existing data")

            with self.assertRaises(SystemExit):
                main(["assemble", str(source)])

            self.assertEqual(output.read_bytes(), b"existing data")


if __name__ == "__main__":
    unittest.main()
