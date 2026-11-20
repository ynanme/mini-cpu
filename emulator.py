from isa import *
from decoder import decode_instruction


def _to_signed(value: int) -> int:
    """Interpret a 32-bit value as a signed integer."""

    sign_bit = 1 << (WORD_SIZE - 1)

    if value & sign_bit:
        return value - (1 << WORD_SIZE)

    return value


class CPU:
    """A simple 32-bit CPU emulator."""

    def __init__(self):
        self.registers = [0] * REGISTER_COUNT
        self.memory = [0] * MEMORY_SIZE
        self.pc = 0

    def write_register(self, index: int, value: int) -> None:
        """Write a 32-bit value to a register."""

        if index == 0:
            return

        if not 0 <= index < REGISTER_COUNT:
            raise ValueError(f"Invalid register: {index}")

        self.registers[index] = value & WORD_MASK

    def execute_instruction(self, instruction: int) -> None:
        """Decode and execute a machine instruction."""

        operation, r1, r2, operand = decode_instruction(instruction)

        if operation not in R_TYPE_OPERATIONS:
            raise NotImplementedError(
                f"Unsupported instruction: {operation}"
            )

        a = self.registers[r2]
        b = self.registers[operand]

        if operation == "add":
            result = a + b

        elif operation == "sub":
            result = a - b

        elif operation == "mul":
            result = a * b

        elif operation == "div":
            a = _to_signed(a)
            b = _to_signed(b)

            if b == 0:
                raise ZeroDivisionError("Division by zero")

            quotient = abs(a) // abs(b)

            result = -quotient if (a < 0) != (b < 0) else quotient

        elif operation == "and":
            result = a & b

        elif operation == "or":
            result = a | b

        elif operation == "xor":
            result = a ^ b

        self.write_register(r1, result)
