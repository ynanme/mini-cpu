from isa import REGISTER_COUNT, MEMORY_SIZE, WORD_MASK


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
