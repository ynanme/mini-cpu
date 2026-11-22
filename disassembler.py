from decoder import decode_instruction

from isa import *


def disassemble_instruction(instruction: int) -> str:
    """Convert a machine instruction into assembly text."""

    operation, r1, r2, operand = decode_instruction(instruction)

    if operation in R_TYPE_OPERATIONS:
        return f"{operation} ${r1}, ${r2}, ${operand}"

    if operation in MEMORY_OPERATIONS:
        return f"{operation} ${r1}, {operand}(${r2})"

    return f"{operation} ${r1}, ${r2}, {operand}"


def disassemble_program(instructions: list[int]) -> str:
    """Convert a machine-code program into assembly text."""

    decoded = [
        decode_instruction(instruction)
        for instruction in instructions
    ]

    labels = {
        operand: f"label_{operand}"
        for operation, _, _, operand in decoded
        if operation in BRANCH_OPERATIONS
        and 0 <= operand <= len(instructions)
    }

    lines = []

    for address, (instruction, decoded_instruction) in enumerate(
        zip(instructions, decoded)
    ):
        operation, r1, r2, operand = decoded_instruction

        if address in labels:
            lines.append(f"{labels[address]}:")

        if operation in BRANCH_OPERATIONS and operand in labels:
            assembly = f"{operation} ${r1}, ${r2}, {labels[operand]}"
        else:
            assembly = disassemble_instruction(instruction)

        lines.append(f"    {assembly}")

    if len(instructions) in labels:
        lines.append(f"{labels[len(instructions)]}:")

    return "\n".join(lines)
