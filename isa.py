# CPU architecture
WORD_SIZE = 32
REGISTER_COUNT = 64

# Instruction encoding
INSTRUCTION_SIZE = 32
OPCODE_SIZE = 5
REGISTER_ID_SIZE = 6
IMMEDIATE_SIZE = 12


# Instruction opcodes
OPCODES = {
    # Register operations
    "add": 0,
    "sub": 1,
    "mul": 2,
    "div": 3,
    "and": 4,
    "or": 5,
    "xor": 6,

    # Immediate operations
    "addi": 7,
    "subi": 8,
    "muli": 9,
    "divi": 10,
    "andi": 11,
    "ori": 12,
    "xori": 13,

    # Memory operations
    "lw": 14,
    "sw": 15,

    # Branch operations
    "beq": 16,
    "bne": 17,
    "blo": 18,
    "bgt": 19,
}


# Instruction field sizes
R_PADDING_SIZE = 9
I_PADDING_SIZE = 3

# Instruction field positions
OPCODE_SHIFT = 27
R1_SHIFT = 21
R2_SHIFT = 15
R3_SHIFT = R_PADDING_SIZE
IMMEDIATE_SHIFT = I_PADDING_SIZE

# Bit masks
OPCODE_MASK = (1 << OPCODE_SIZE) - 1
REGISTER_MASK = (1 << REGISTER_ID_SIZE) - 1
IMMEDIATE_MASK = (1 << IMMEDIATE_SIZE) - 1

# Operation types
R_TYPE_OPERATIONS = {
    "add", "sub", "mul", "div",
    "and", "or", "xor"
}
SIGNED_IMMEDIATE_OPERATIONS = {
    "addi", "subi", "muli", "divi"
}
UNSIGNED_IMMEDIATE_OPERATIONS = {
    "andi", "ori", "xori"
}
