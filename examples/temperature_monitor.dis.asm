    addi $1, $0, 100
    addi $2, $0, -4
    sw $2, 0($1)
    addi $2, $0, 12
    sw $2, 1($1)
    addi $2, $0, 18
    sw $2, 2($1)
    addi $2, $0, 45
    sw $2, 3($1)
    addi $2, $0, 7
    sw $2, 4($1)
    addi $2, $0, 39
    sw $2, 5($1)
    addi $2, $0, -3
    sw $2, 6($1)
    addi $2, $0, 20
    sw $2, 7($1)
    add $3, $1, $0
    add $4, $0, $0
    add $5, $0, $0
    addi $7, $0, 8
    lw $8, 0($1)
    add $9, $8, $0
    add $10, $0, $0
    addi $11, $0, 30
    add $12, $0, $0
    add $15, $0, $0
label_27:
    lw $6, 0($3)
    add $5, $5, $6
    bgt $6, $8, label_32
    beq $6, $8, label_32
    add $8, $6, $0
label_32:
    bgt $9, $6, label_36
    beq $9, $6, label_36
    add $9, $6, $0
    add $10, $4, $0
label_36:
    bgt $11, $6, label_40
    beq $11, $6, label_40
    addi $12, $12, 1
    ori $15, $15, 1
label_40:
    bgt $6, $0, label_43
    beq $6, $0, label_43
    ori $15, $15, 2
label_43:
    addi $3, $3, 1
    addi $4, $4, 1
    bne $4, $7, label_27
    divi $13, $5, 8
    sw $5, 200($0)
    sw $13, 201($0)
    sw $8, 202($0)
    sw $9, 203($0)
    sw $12, 204($0)
    sw $15, 205($0)
    sw $10, 206($0)
