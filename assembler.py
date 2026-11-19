import re

from isa import *


def encode_r_type(operation: str, r1: int, r2: int, r3: int) -> int:
    """Encode an R-type instruction into a 32-bit integer."""

    if operation not in R_TYPE_OPERATIONS:
        raise ValueError(f"Invalid R-type operation: {operation}")

    for register in (r1, r2, r3):
        if not 0 <= register < REGISTER_COUNT:
            raise ValueError(f"Invalid register: {register}")

    return (
        (OPCODES[operation] << OPCODE_SHIFT)
        | (r1 << R1_SHIFT)
        | (r2 << R2_SHIFT)
        | (r3 << R3_SHIFT)
    )


def _encode_i_format(operation: str, r1: int, r2: int, immediate: int, *, signed: bool) -> int:
    """Encode an instruction using the I-format layout."""

    for register in (r1, r2):
        if not 0 <= register < REGISTER_COUNT:
            raise ValueError(f"Invalid register: {register}")

    if signed:
        minimum = -(1 << (IMMEDIATE_SIZE - 1))
        maximum = (1 << (IMMEDIATE_SIZE - 1)) - 1
    else:
        minimum = 0
        maximum = IMMEDIATE_MASK

    if not minimum <= immediate <= maximum:
        raise ValueError(f"Immediate out of range: {immediate}")

    encoded_immediate = immediate & IMMEDIATE_MASK

    return (
        (OPCODES[operation] << OPCODE_SHIFT)
        | (r1 << R1_SHIFT)
        | (r2 << R2_SHIFT)
        | (encoded_immediate << IMMEDIATE_SHIFT)
    )


def encode_i_type(operation: str, r1: int, r2: int, immediate: int) -> int:
    """Encode an immediate arithmetic or logical instruction."""

    if operation not in (
        SIGNED_IMMEDIATE_OPERATIONS | UNSIGNED_IMMEDIATE_OPERATIONS
    ):
        raise ValueError(f"Invalid I-type operation: {operation}")

    return _encode_i_format(operation, r1, r2, immediate, signed=operation in SIGNED_IMMEDIATE_OPERATIONS)


def encode_memory_type(operation: str, r1: int, r2: int, offset: int) -> int:
    """Encode a memory load or store instruction."""

    if operation not in MEMORY_OPERATIONS:
        raise ValueError(f"Invalid memory operation: {operation}")

    return _encode_i_format(operation, r1, r2, offset, signed=True)


def encode_branch_type(operation: str, r1: int, r2: int, address: int) -> int:
    """Encode a conditional branch instruction."""

    if operation not in BRANCH_OPERATIONS:
        raise ValueError(f"Invalid branch operation: {operation}")

    return _encode_i_format(operation, r1, r2, address, signed=False)


def _parse_register(token: str) -> int:
    """Parse and validate a register operand."""

    if not re.fullmatch(r"\$\d+", token):
        raise ValueError(f"Invalid register syntax: {token}")

    register = int(token[1:])

    if not 0 <= register < REGISTER_COUNT:
        raise ValueError(f"Invalid register: {register}")

    return register


def parse_instruction(line: str) -> tuple:
    """Parse a single assembly instruction."""

    # Remove comments and surrounding whitespace
    line = line.split("#", 1)[0].strip()

    parts = line.split(maxsplit=1)

    if len(parts) != 2:
        raise ValueError(f"Invalid instruction: {line}")

    operation, raw_operands = parts

    if operation not in OPCODES:
        raise ValueError(f"Unknown instruction: {operation}")

    operands = [operand.strip() for operand in raw_operands.split(",")]

    # Memory instructions: lw r1, offset(r2)
    if operation in MEMORY_OPERATIONS:
        if len(operands) != 2:
            raise ValueError("Memory instructions require 2 operands")

        r1 = _parse_register(operands[0])

        match = re.fullmatch(
            r"([+-]?\d+)?\s*\(\s*(\$\d+)\s*\)",
            operands[1],
        )

        if not match:
            raise ValueError(f"Invalid memory operand: {operands[1]}")

        offset = int(match.group(1) or 0)
        r2 = _parse_register(match.group(2))

        return operation, r1, r2, offset

    # Other instructions require 3 operands
    if len(operands) != 3:
        raise ValueError(f"{operation} requires 3 operands")

    r1 = _parse_register(operands[0])
    r2 = _parse_register(operands[1])

    # Register instructions
    if operation in R_TYPE_OPERATIONS:
        r3 = _parse_register(operands[2])
        return operation, r1, r2, r3

    # Branch instructions
    if operation in BRANCH_OPERATIONS:
        target = operands[2]

        if re.fullmatch(r"[+-]?\d+", target):
            return operation, r1, r2, int(target)

        if not re.fullmatch(r"[A-Za-z_]\w*", target):
            raise ValueError(f"Invalid branch target: {target}")

        return operation, r1, r2, target

    # Immediate instructions
    immediate = int(operands[2])

    return operation, r1, r2, immediate
