# Count down from 5 to 0

    addi $1, $0, 5

loop:
    subi $1, $1, 1
    bne $1, $0, loop
