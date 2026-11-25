# Mini CPU

A custom 32-bit instruction set architecture (ISA) with a Python assembler, CPU emulator, and disassembler.

Mini CPU aims to explore how assembly instructions are encoded, decoded, and executed by a processor.

It implements a custom 20-instruction ISA, a 64-register CPU, word-addressable memory, and conditional branching.

The toolchain supports three operations:

- **Assemble** — Convert assembly source code into 32-bit machine instructions.
- **Run** — Execute compiled programs on the CPU emulator.
- **Disassemble** — Reconstruct assembly code from machine instructions, including generated labels for branch targets.

## Getting Started

### Requirements

- Python 3.10 or later
- No external Python dependencies

### Setup

Clone the repository:

```bash
git clone https://github.com/ynanme/mini-cpu.git
cd mini-cpu
```

### Usage

**Assemble a program:**

```bash
./mcpu.py assemble examples/temperature_monitor.asm
```

This produces `examples/temperature_monitor.bin`, containing the compiled instructions as 32-bit words.

To also generate a human-readable binary representation:

```bash
./mcpu.py assemble examples/temperature_monitor.asm --emit-bits
```

This additionally creates `examples/temperature_monitor.bits`, with one 32-bit instruction per line.

**Run a program:**

```bash
./mcpu.py run examples/temperature_monitor.bin
```

The emulator executes the program and reports the number of executed instructions, the final program counter, and all non-zero registers.

**Disassemble a program:**

```bash
./mcpu.py disassemble examples/temperature_monitor.bin
```

This produces `examples/temperature_monitor.dis.asm`.

Original source labels and comments cannot be recovered from machine code. The disassembler generates labels from branch target addresses instead.

All generated files are written alongside their input files. Existing output files with the same names are overwritten.

To see all available commands:

```bash
./mcpu.py --help
```


## Instruction Set Architecture

Mini CPU implements a custom ISA with 20 instructions, 64 registers (`$0`–`$63`), and fixed-width 32-bit instructions.

Instructions fall into four categories: register operations, immediate operations, memory access, and conditional branches.

### Arithmetic and Logical Operations

Register operations follow the syntax `op $d, $a, $b`, while immediate operations replace the second source register with a constant: `opi $d, $a, imm`.

The result is stored in the destination register `$d`.

| Operation | Register (opcode) | Immediate (opcode) | Computation |
|---|---|---|---|
| Addition | `add` (0) | `addi` (7) | `a + b` |
| Subtraction | `sub` (1) | `subi` (8) | `a - b` |
| Multiplication | `mul` (2) | `muli` (9) | `a * b` |
| Division | `div` (3) | `divi` (10) | `a / b` |
| Bitwise AND | `and` (4) | `andi` (11) | `a & b` |
| Bitwise OR | `or` (5) | `ori` (12) | `a \| b` |
| Bitwise XOR | `xor` (6) | `xori` (13) | `a ^ b` |

Division is signed integer division with truncation toward zero. Arithmetic results are stored modulo \(2^{32}\).

### Memory Operations

Memory instructions use base-plus-offset addressing.

| Instruction | Opcode | Syntax | Effect |
|---|---:|---|---|
| `lw` | 14 | `lw $d, offset($base)` | `$d = memory[$base + offset]` |
| `sw` | 15 | `sw $s, offset($base)` | `memory[$base + offset] = $s` |

The offset is optional and defaults to zero, e.g. `lw $1, ($2)`.

Memory addresses refer to **32-bit words**, not individual bytes.

### Conditional Branches

Branches follow the syntax `op $a, $b, target`.

| Instruction | Opcode | Branch condition |
|---|---:|---|
| `beq` | 16 | `a == b` |
| `bne` | 17 | `a != b` |
| `blo` | 18 | `a < b` (unsigned) |
| `bgt` | 19 | `a > b` (signed) |

Branch targets are **absolute instruction indices**, specified either numerically or through labels.

Labels are resolved during assembly. They may be defined on their own line or before an instruction.

### Immediate Values

Immediate fields are 12 bits wide, with different interpretations depending on the instruction.

| Instructions | Interpretation | Allowed range |
|---|---|---|
| `addi`, `subi`, `muli`, `divi` | Signed | −2048 to 2047 |
| `andi`, `ori`, `xori` | Unsigned | 0 to 4095 |
| `lw`, `sw` | Signed offset | −2048 to 2047 |
| `beq`, `bne`, `blo`, `bgt` | Unsigned address | 0 to 4095 |

A branch target must also be within the loaded program or exactly one instruction past its end.

### Instruction Encoding

Every instruction occupies exactly 32 bits and uses one of two formats:

**R-type — Register operations**

```text
31      27 26      21 20      15 14       9 8        0
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ Opcode:5 │  r1:6    │  r2:6    │  r3:6    │ Zero:9   │
└──────────┴──────────┴──────────┴──────────┴──────────┘
```

**I-format — Immediate, memory, and branch operations**

```text
31      27 26      21 20      15 14            3 2    0
┌──────────┬──────────┬──────────┬────────────────┬──────┐
│ Opcode:5 │  r1:6    │  r2:6    │ Immediate:12   │Zero:3│
└──────────┴──────────┴──────────┴────────────────┴──────┘
```

Unused bits are set to zero. The decoder rejects instructions with non-zero reserved bits.

The assembler supports `#` comments, blank lines, and symbolic labels.


## Architecture & Design Decisions

Mini CPU implements a simplified 32-bit load/store architecture. The following conventions define how instructions and data are represented and executed.

### CPU Model

| Component | Specification |
|---|---|
| Registers | 64 general-purpose registers, 32 bits each |
| Zero register | `$0` always reads as zero; writes are ignored |
| Data memory | 1024 words of 32 bits (4 KiB) |
| Memory addressing | Word-addressable, using zero-based indices |
| Program memory | Separate from data memory |
| Program counter | Zero-based instruction index |
| Branch addressing | Absolute instruction indices |
| Instruction width | Fixed at 32 bits |

Registers and data memory are initialized to zero when a CPU instance is created.

Program instructions are stored separately from data. Consequently, `lw` and `sw` access only data memory and cannot modify executable instructions.

### Integer Representation

Registers store 32-bit values. Arithmetic results wrap around modulo \(2^{32}\), and signed integers use two's complement.

For example, `-1` is represented by the bit pattern `0xFFFFFFFF`.

The emulator stores register values as unsigned Python integers, interpreting them as signed values only when required by an operation.

The CLI displays raw register values in unsigned decimal form.

### Program Execution

Execution starts at instruction index `0` and follows a **fetch–decode–execute** cycle.

The program counter advances by one after each instruction, unless a taken branch specifies a different address.

Mini CPU has no dedicated `halt` instruction. Execution terminates when the program counter reaches the index immediately after the last instruction (`PC == len(program)`).

A branch to this position is valid and can be used to terminate a program.

Loading a new program resets the program counter but does not clear the existing registers or data memory. The CLI creates a fresh CPU instance for each execution.

### Runtime Behavior

- **Invalid memory access:** Raises `IndexError`.
- **Invalid program counter or branch target:** Raises `IndexError`.
- **Invalid instruction encoding:** Raises `ValueError`.
- **Division by zero:** Raises `ZeroDivisionError`.
- **Infinite loops:** Continue executing until externally interrupted; no automatic instruction limit is imposed.

### Machine Code Format

Compiled `.bin` files contain raw 32-bit instructions stored as four bytes each, in **big-endian** byte order.

The optional `.bits` format provides a human-readable representation, with one 32-bit binary instruction per line.


## Example: Industrial Temperature Monitor

The repository includes a temperature monitoring application written entirely in Mini CPU assembly.

The program initializes eight simulated temperature readings, processes them in a single loop, and computes statistics and alert conditions.

### Algorithm

The assembly program implements the equivalent of the following Python-like pseudocode:

```python
samples = [-4, 12, 18, 45, 7, 39, -3, 20]

total = 0
minimum = maximum = samples[0]
max_index = 0
high_count = 0
status = 0

for index, temperature in enumerate(samples):
    total += temperature

    if temperature < minimum:
        minimum = temperature

    if temperature > maximum:
        maximum = temperature
        max_index = index

    if temperature > 30:
        high_count += 1
        status |= 0b01

    if temperature < 0:
        status |= 0b10

average = int(total / len(samples))  # Truncate toward zero
```

All processing is performed by the emulated CPU using its own instruction set, with Python performing the computations.

### Results

The program stores its results in data memory:

| Address | Result | Value |
|---|---|---:|
| 200 | Sum | 134 |
| 201 | Integer average | 16 |
| 202 | Minimum | -4 |
| 203 | Maximum | 45 |
| 204 | Readings above 30°C | 2 |
| 205 | Status flags | 3 |
| 206 | Maximum index | 3 |

The status word uses two flags: bit 0 indicates overheating, while bit 1 indicates a negative temperature. A value of `3` means both conditions were detected.

### Run the Example

```bash
./mcpu.py assemble examples/temperature_monitor.asm
./mcpu.py run examples/temperature_monitor.bin
```

The CLI reports execution statistics and non-zero registers; the full results are stored in data memory.

The CLI does not display data memory directly.

The original assembly source, compiled binary, and reconstructed assembly are available in [`examples/`](examples/).


## Testing

Mini CPU includes unit and integration tests covering:

- Instruction encoding and decoding, including invalid encodings.
- Arithmetic, logical, memory, and branch operations.
- Register behavior, signed arithmetic, and error handling.
- Assembly/disassembly round trips.
- End-to-end execution of all 20 instructions.
- Temperature monitoring across multiple input scenarios.

Run the complete test suite with:

```bash
python3 -m unittest discover -s tests -v
```

Tests use Python's built-in `unittest` framework and require no external dependencies.

## Project Structure

```text
mini-cpu/
├── mcpu.py              # Command-line interface
├── isa.py               # ISA definitions and opcodes
├── assembler.py         # Assembly to machine code
├── decoder.py           # Instruction decoding
├── emulator.py          # CPU execution and memory
├── disassembler.py      # Machine code to assembly
├── machine_code.py      # Binary serialization
├── examples/            # Example assembly programs
├── tests/               # Unit and integration tests
└── README.md
```

The modules can be used independently through Python, while `mcpu.py` provides the main command-line interface.
