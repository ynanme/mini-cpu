from pathlib import Path

from isa import INSTRUCTION_SIZE


INSTRUCTION_BYTES = INSTRUCTION_SIZE // 8


def write_machine_code(path: str | Path, instructions: list[int]) -> None:
    """Write 32-bit machine instructions to a binary file."""

    data = bytearray()

    for instruction in instructions:
        if not 0 <= instruction < (1 << INSTRUCTION_SIZE):
            raise ValueError(f"Invalid instruction value: {instruction}")

        data.extend(
            instruction.to_bytes(INSTRUCTION_BYTES, byteorder="big")
        )

    Path(path).write_bytes(data)


def read_machine_code(path: str | Path) -> list[int]:
    """Read 32-bit machine instructions from a binary file."""

    data = Path(path).read_bytes()

    if len(data) % INSTRUCTION_BYTES != 0:
        raise ValueError("Invalid machine code file size")

    instructions = []

    for offset in range(0, len(data), INSTRUCTION_BYTES):
        instruction = int.from_bytes(
            data[offset:offset + INSTRUCTION_BYTES],
            byteorder="big",
        )

        instructions.append(instruction)

    return instructions
