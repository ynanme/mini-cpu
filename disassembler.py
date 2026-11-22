from decoder import decode_instruction

from isa import (
    R_TYPE_OPERATIONS,
    MEMORY_OPERATIONS,
    BRANCH_OPERATIONS,
)


def disassemble_instruction(instruction: int) -> str:
    """Convert a machine instruction into assembly text."""

    operation, r1, r2, operand = decode_instruction(instruction)

    if operation in R_TYPE_OPERATIONS:
        return f"{operation} ${r1}, ${r2}, ${operand}"

    if operation in MEMORY_OPERATIONS:
        return f"{operation} ${r1}, {operand}(${r2})"

    return f"{operation} ${r1}, ${r2}, {operand}"
