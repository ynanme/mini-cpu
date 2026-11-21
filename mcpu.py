#!/usr/bin/env python3

import argparse

from pathlib import Path

from assembler import assemble_program
from emulator import CPU
from machine_code import read_machine_code, write_machine_code


def main(argv: list[str] | None = None) -> int:
    """Run the Mini CPU command-line interface."""

    parser = argparse.ArgumentParser(
        description="Mini CPU toolchain"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    assemble_parser = subparsers.add_parser(
        "assemble",
        help="Assemble source code into machine code",
    )

    assemble_parser.add_argument(
        "input",
        type=Path,
        help="Assembly source file",
    )

    assemble_parser.add_argument(
        "--emit-bits",
        action="store_true",
        help="Also generate a human-readable binary file",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Execute a compiled machine-code program",
    )

    run_parser.add_argument(
        "binary",
        type=Path,
        help="Path to the machine-code file",
    )

    args = parser.parse_args(argv)

    if args.command == "assemble":
        source_path = args.input
        output_path = source_path.with_suffix(".bin")

        try:
            source = source_path.read_text(encoding="utf-8")
            machine_code = assemble_program(source)

            write_machine_code(output_path, machine_code)

            if args.emit_bits:
                bits_path = source_path.with_suffix(".bits")

                bits = "".join(
                    f"{instruction:032b}\n"
                    for instruction in machine_code
                )

                bits_path.write_text(bits, encoding="utf-8")

        except (OSError, ValueError) as error:
            parser.error(str(error))

        print(f"Assembled {len(machine_code)} instructions into {output_path}")

    elif args.command == "run":
        instructions = read_machine_code(args.binary)

        cpu = CPU()
        cpu.load_program(instructions)

        steps = cpu.run()

        print(f"Instructions executed: {steps}")
        print(f"Final PC: {cpu.pc}")

        print("\nNon-zero registers:")

        found = False

        for index, value in enumerate(cpu.registers):
            if value != 0:
                print(f"${index} = {value}")
                found = True

        if not found:
            print("(none)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
