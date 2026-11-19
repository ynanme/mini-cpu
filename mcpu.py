import argparse

from pathlib import Path

from assembler import assemble_program
from machine_code import write_machine_code


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
        "-o", "--output",
        type=Path,
        help="Output machine code file",
    )

    args = parser.parse_args(argv)

    if args.command == "assemble":
        source_path = args.input
        output_path = args.output or source_path.with_suffix(".bin")

        if output_path.exists():
            parser.error(f"Output file already exists: {output_path}")

        try:
            source = source_path.read_text(encoding="utf-8")
            machine_code = assemble_program(source)
            write_machine_code(output_path, machine_code)
        except (OSError, ValueError) as error:
            parser.error(str(error))

        print(f"Assembled {len(machine_code)} instructions into {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
