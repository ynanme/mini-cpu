from isa import *


OPCODE_NAMES = {code: name for name, code in OPCODES.items()}


def decode_instruction(instruction: int) -> tuple[str, int, int, int]:
    """Decode a 32-bit machine instruction."""

    if not 0 <= instruction < (1 << INSTRUCTION_SIZE):
        raise ValueError(f"Invalid instruction value: {instruction}")

    opcode = (instruction >> OPCODE_SHIFT) & OPCODE_MASK

    if opcode not in OPCODE_NAMES:
        raise ValueError(f"Unknown opcode: {opcode}")

    operation = OPCODE_NAMES[opcode]

    r1 = (instruction >> R1_SHIFT) & REGISTER_MASK
    r2 = (instruction >> R2_SHIFT) & REGISTER_MASK

    if operation in R_TYPE_OPERATIONS:
        if instruction & ((1 << R_PADDING_SIZE) - 1):
            raise ValueError("Non-zero reserved bits")

        r3 = (instruction >> R3_SHIFT) & REGISTER_MASK

        return operation, r1, r2, r3

    if instruction & ((1 << I_PADDING_SIZE) - 1):
        raise ValueError("Non-zero reserved bits")

    immediate = (instruction >> IMMEDIATE_SHIFT) & IMMEDIATE_MASK

    if operation in SIGNED_IMMEDIATE_OPERATIONS | MEMORY_OPERATIONS:
        sign_bit = 1 << (IMMEDIATE_SIZE - 1)

        if immediate & sign_bit:
            immediate -= 1 << IMMEDIATE_SIZE

    return operation, r1, r2, immediate
