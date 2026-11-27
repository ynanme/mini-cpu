#!/usr/bin/env python3

import argparse
from pathlib import Path

from assembler import assemble_program
from disassembler import disassemble_program
from emulator import CPU
from machine_code import read_machine_code, write_machine_code


def parse_selection(spec: str, size: int) -> list[int]:
    """Parse indices and half-open ranges, preserving order without duplicates."""
    indices = []
    seen = set()

    for part in spec.split(","):
        if ":" in part:
            bounds = part.split(":")
            if len(bounds) != 2 or not all(bound.isdecimal() for bound in bounds):
                raise argparse.ArgumentTypeError(f"Invalid selection: {part!r}")

            start, end = map(int, bounds)
            if not 0 <= start < end <= size:
                raise argparse.ArgumentTypeError(
                    f"Range {part!r} must satisfy 0 <= start < end <= {size}"
                )
            selected = range(start, end)
        else:
            if not part.isdecimal():
                raise argparse.ArgumentTypeError(f"Invalid index: {part!r}")

            index = int(part)
            if not 0 <= index < size:
                raise argparse.ArgumentTypeError(
                    f"Index {index} must be between 0 and {size - 1}"
                )
            selected = (index,)

        for index in selected:
            if index not in seen:
                seen.add(index)
                indices.append(index)

    return indices


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
    run_parser.add_argument(
        "--registers",
        type=lambda spec: parse_selection(spec, 64),
        metavar="SELECTION",
        help="Inspect registers (e.g. 1,3,7 or 1:10)",
    )
    run_parser.add_argument(
        "--memory",
        type=lambda spec: parse_selection(spec, 1024),
        metavar="SELECTION",
        help="Inspect memory words (e.g. 100,200:207)",
    )

    disassemble_parser = subparsers.add_parser(
        "disassemble",
        help="Convert machine code into assembly",
    )

    disassemble_parser.add_argument(
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

        if args.registers is None:
            print("\nNon-zero registers:")
            found = False
            for index, value in enumerate(cpu.registers):
                if value != 0:
                    print(f"${index} = {value}")
                    found = True
            if not found:
                print("(none)")
        else:
            print("\nSelected registers:")
            for index in args.registers:
                print(f"${index} = {cpu.registers[index]}")

        if args.memory is not None:
            print("\nSelected memory:")
            for index in args.memory:
                print(f"[{index}] = {cpu.memory[index]}")

    elif args.command == "disassemble":
        instructions = read_machine_code(args.binary)

        assembly = disassemble_program(instructions)

        output = args.binary.with_suffix(".dis.asm")
        output.write_text(assembly + "\n", encoding="utf-8")

        print(f"Disassembled {len(instructions)} instructions into {output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
