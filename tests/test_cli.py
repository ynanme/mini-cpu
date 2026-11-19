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

    def test_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "program.asm"
            output = source.with_suffix(".bin")

            source.write_text("addi $1, $0, 5\n")
            main(["assemble", str(source)])

            original = output.read_bytes()

            source.write_text("addi $1, $0, 10\n")
            main(["assemble", str(source)])

            self.assertNotEqual(output.read_bytes(), original)
            self.assertEqual(
                read_machine_code(output),
                assemble_program(source.read_text()),
        )

    def test_emit_bits(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "program.asm"
            source.write_text(
                "addi $1, $0, 5\n"
                "add $2, $1, $1\n"
            )

            main(["assemble", str(source), "--emit-bits"])

            bits_path = source.with_suffix(".bits")
            machine_code = assemble_program(source.read_text())

            expected = "".join(
                f"{instruction:032b}\n"
                for instruction in machine_code
            )

            self.assertTrue(bits_path.exists())
            self.assertEqual(bits_path.read_text(), expected)
    
    def test_no_bits_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "program.asm"
            source.write_text("addi $1, $0, 5\n")

            main(["assemble", str(source)])

            self.assertFalse(source.with_suffix(".bits").exists())


if __name__ == "__main__":
    unittest.main()
