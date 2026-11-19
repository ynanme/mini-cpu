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


def encode_i_type(operation: str, r1: int, r2: int, immediate: int) -> int:
    """Encode an I-type arithmetic or logical instruction."""

    if operation not in (
        SIGNED_IMMEDIATE_OPERATIONS | UNSIGNED_IMMEDIATE_OPERATIONS
    ):
        raise ValueError(f"Invalid I-type operation: {operation}")

    for register in (r1, r2):
        if not 0 <= register < REGISTER_COUNT:
            raise ValueError(f"Invalid register: {register}")

    if operation in SIGNED_IMMEDIATE_OPERATIONS:
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
