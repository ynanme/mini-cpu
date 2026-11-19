from isa import (
    OPCODES,
    R_TYPE_OPERATIONS,
    REGISTER_COUNT,
    OPCODE_SHIFT,
    R1_SHIFT,
    R2_SHIFT,
    R3_SHIFT,
)


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
