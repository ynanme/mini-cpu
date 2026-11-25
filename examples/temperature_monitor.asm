# Industrial Temperature Monitor
#
# Input data:
#   Eight temperature samples stored at addresses 100-107.
#
# Output data:
#   Results will be stored at addresses 200-206.
#
# Registers:
#   $1 - Base address of the temperature array
#   $2 - Temporary register for sample initialization


# --------------------------------------------------
# 1. Initialize temperature samples
# --------------------------------------------------

    addi $1, $0, 100

    # Temperature 0: -4
    addi $2, $0, -4
    sw $2, 0($1)

    # Temperature 1: 12
    addi $2, $0, 12
    sw $2, 1($1)

    # Temperature 2: 18
    addi $2, $0, 18
    sw $2, 2($1)

    # Temperature 3: 45
    addi $2, $0, 45
    sw $2, 3($1)

    # Temperature 4: 7
    addi $2, $0, 7
    sw $2, 4($1)

    # Temperature 5: 39
    addi $2, $0, 39
    sw $2, 5($1)

    # Temperature 6: -3
    addi $2, $0, -3
    sw $2, 6($1)

    # Temperature 7: 20
    addi $2, $0, 20
    sw $2, 7($1)


# --------------------------------------------------
# 2. Traverse samples and compute statistics
# --------------------------------------------------

    # Initialize traversal state
    add $3, $1, $0
    add $4, $0, $0
    add $5, $0, $0
    addi $7, $0, 8

    # Initialize extrema with the first sample
    lw $8, ($1)
    add $9, $8, $0
    add $10, $0, $0

    # Initialize monitoring state
    addi $11, $0, 30
    add $12, $0, $0
    add $15, $0, $0

sum_loop:
    # Load current temperature
    lw $6, ($3)

    # Accumulate temperature
    add $5, $5, $6

    # Update minimum
    bgt $6, $8, min_done
    beq $6, $8, min_done

    add $8, $6, $0

min_done:
    # Update maximum and its index
    bgt $9, $6, max_done
    beq $9, $6, max_done

    add $9, $6, $0
    add $10, $4, $0

max_done:
    # Count temperatures strictly above the threshold
    bgt $11, $6, high_done
    beq $11, $6, high_done

    addi $12, $12, 1
    ori $15, $15, 1

high_done:
    # Flag negative temperatures
    bgt $6, $0, negative_done
    beq $6, $0, negative_done

    ori $15, $15, 2

negative_done:
    # Move to the next sample
    addi $3, $3, 1
    addi $4, $4, 1

    # Continue until all samples are processed
    bne $4, $7, sum_loop

    # Compute the integer average
    divi $13, $5, 8

    # Store monitoring results
    sw $5, 200($0)
    sw $13, 201($0)
    sw $8, 202($0)
    sw $9, 203($0)
    sw $12, 204($0)
    sw $15, 205($0)
    sw $10, 206($0)
    