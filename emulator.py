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
        self.program = []
    
    def load_program(self, program: list[int]) -> None:
        """Load machine instructions and reset the program counter."""

        self.program = list(program)
        self.pc = 0
    
    def run(self) -> int:
        """Run the loaded program until completion."""

        steps = 0

        while self.step():
            steps += 1

        return steps

    def step(self) -> bool:
        """Execute the next instruction and update the program counter."""

        if self.pc == len(self.program):
            return False

        if not 0 <= self.pc < len(self.program):
            raise IndexError(f"Invalid program counter: {self.pc}")

        instruction = self.program[self.pc]

        target = self.execute_instruction(instruction)

        next_pc = self.pc + 1 if target is None else target

        if not 0 <= next_pc <= len(self.program):
            raise IndexError(f"Invalid branch target: {next_pc}")

        self.pc = next_pc

        return True

    def write_register(self, index: int, value: int) -> None:
        """Write a 32-bit value to a register."""

        if index == 0:
            return

        if not 0 <= index < REGISTER_COUNT:
            raise ValueError(f"Invalid register: {index}")

        self.registers[index] = value & WORD_MASK

    def execute_instruction(self, instruction: int) -> int | None:
        """Execute an instruction and return its branch target if taken."""

        operation, r1, r2, operand = decode_instruction(instruction)

        if operation in MEMORY_OPERATIONS:
            address = self.registers[r2] + operand

            if not 0 <= address < MEMORY_SIZE:
                raise IndexError(f"Invalid memory address: {address}")

            if operation == "lw":
                self.write_register(r1, self.memory[address])

            elif operation == "sw":
                self.memory[address] = self.registers[r1]

            return
        
        if operation in BRANCH_OPERATIONS:
            a = self.registers[r1]
            b = self.registers[r2]

            if operation == "beq":
                taken = a == b

            elif operation == "bne":
                taken = a != b

            elif operation == "blo":
                taken = a < b

            elif operation == "bgt":
                taken = _to_signed(a) > _to_signed(b)

            return operand if taken else None

        is_r_type = operation in R_TYPE_OPERATIONS
        is_i_type = operation in (
            SIGNED_IMMEDIATE_OPERATIONS | UNSIGNED_IMMEDIATE_OPERATIONS
        )

        if not (is_r_type or is_i_type):
            raise NotImplementedError(f"Unsupported instruction: {operation}")

        a = self.registers[r2]
        b = self.registers[operand] if is_r_type else operand

        base_operation = operation[:-1] if is_i_type else operation

        if base_operation == "add":
            result = a + b

        elif base_operation == "sub":
            result = a - b

        elif base_operation == "mul":
            result = a * b

        elif base_operation == "div":
            a = _to_signed(a)
            b = _to_signed(b & WORD_MASK)

            if b == 0:
                raise ZeroDivisionError("Division by zero")

            quotient = abs(a) // abs(b)

            result = -quotient if (a < 0) != (b < 0) else quotient

        elif base_operation == "and":
            result = a & b

        elif base_operation == "or":
            result = a | b

        elif base_operation == "xor":
            result = a ^ b

        self.write_register(r1, result)
