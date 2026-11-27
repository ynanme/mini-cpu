import argparse
import subprocess
import sys
import tempfile
import unittest
import tempfile

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from assembler import assemble_program
from machine_code import read_machine_code, write_machine_code
from mcpu import main, parse_selection


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


class TestRunCLI(unittest.TestCase):

    def test_run_program(self):
        source = """
            addi $1, $0, 10
            addi $2, $0, 20
            add $3, $1, $2
        """

        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "program.bin"

            write_machine_code(binary, assemble_program(source))

            result = subprocess.run(
                [sys.executable, "mcpu.py", "run", str(binary)],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Instructions executed: 3", result.stdout)
            self.assertIn("Final PC: 3", result.stdout)
            self.assertIn("$3 = 30", result.stdout)

    def test_run_loop(self):
        source = """
            addi $1, $0, 3

        loop:
            subi $1, $1, 1
            bne $1, $0, loop
        """

        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "loop.bin"

            write_machine_code(binary, assemble_program(source))

            result = subprocess.run(
                [sys.executable, "mcpu.py", "run", str(binary)],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Instructions executed: 7", result.stdout)
            self.assertIn("Final PC: 3", result.stdout)


class TestDisassembleCLI(unittest.TestCase):

    def test_disassemble_program(self):
        source = """
            addi $1, $0, 3

        loop:
            subi $1, $1, 1
            bne $1, $0, loop
        """

        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "loop.bin"
            output = Path(tmp) / "loop.dis.asm"

            write_machine_code(binary, assemble_program(source))

            result = subprocess.run(
                [sys.executable, "mcpu.py", "disassemble", str(binary)],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.exists())

            assembly = output.read_text()

            self.assertIn("label_1:", assembly)
            self.assertIn("bne $1, $0, label_1", assembly)

    def test_original_source_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "program.asm"
            binary = Path(tmp) / "program.bin"

            original = "addi $1, $0, 42\n"
            source.write_text(original)

            write_machine_code(binary, assemble_program(original))

            result = subprocess.run(
                [sys.executable, "mcpu.py", "disassemble", str(binary)],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(source.read_text(), original)
            self.assertTrue((Path(tmp) / "program.dis.asm").exists())

    def test_disassembly_round_trip(self):
        source = """
            addi $1, $0, 5

        loop:
            subi $1, $1, 1
            bne $1, $0, loop
            sw $1, 10($0)
        """

        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "program.bin"
            output = Path(tmp) / "program.dis.asm"

            original = assemble_program(source)
            write_machine_code(binary, original)

            result = subprocess.run(
                [sys.executable, "mcpu.py", "disassemble", str(binary)],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)

            reconstructed = assemble_program(output.read_text())

            self.assertEqual(reconstructed, original)


class TestStateInspection(unittest.TestCase):
    
    def test_selection_formats_and_deduplication(self):
        self.assertEqual(parse_selection("1,3,7", 64), [1, 3, 7])
        self.assertEqual(parse_selection("1:4,3,10:12", 64), [1, 2, 3, 10, 11])
        self.assertEqual(parse_selection("0:64", 64), list(range(64)))
        self.assertEqual(parse_selection("1023", 1024), [1023])

    def test_invalid_selections(self):
        for spec, size in (
            ("", 64), ("1,", 64), ("1:1", 64), ("4:2", 64),
            ("64", 64), ("63:65", 64), ("-1", 64), ("1:2:3", 64),
            ("1024", 1024),
        ):
            with self.subTest(spec=spec):
                with self.assertRaises(argparse.ArgumentTypeError):
                    parse_selection(spec, size)

    def test_selected_registers_and_memory_include_zero(self):
        source = """
            addi $1, $0, 7
            sub $2, $1, $1
            sw $2, 200($0)
            addi $3, $0, 42
            sw $3, 201($0)
        """
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "program.bin"
            write_machine_code(binary, assemble_program(source))
            output = StringIO()
            with redirect_stdout(output):
                status = main([
                    "run", str(binary), "--registers", "2,1:3",
                    "--memory", "200:202",
                ])

        self.assertEqual(status, 0)
        self.assertIn("$2 = 0", output.getvalue())
        self.assertIn("$1 = 7", output.getvalue())
        self.assertEqual(output.getvalue().count("$2 = 0"), 1)
        self.assertIn("[200] = 0", output.getvalue())
        self.assertIn("[201] = 42", output.getvalue())

    def test_invalid_cli_selection_exits_before_execution(self):
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as result:
                main(["run", "not-needed.bin", "--memory", "1024"])
        self.assertEqual(result.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
