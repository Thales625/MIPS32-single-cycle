.data
    framebuf: .space 256

    PLAYER_MOVE: .word -1
    PLAYER_Y: .word 8

    BALL_MOVE_Y: .word 1
    BALL_MOVE_X: .word -1
    BALL_X: .word 15
    BALL_Y: .word 8

.eqv SIZE_L1 $r5
.eqv SIZE_SLL2 $r6
.eqv SIZE $r7
.eqv BALL_COLOR $r8
.eqv PLAYER_COLOR $r9

.text
    # const
    ldi SIZE, 16
    sll SIZE_SLL2, SIZE
    sll SIZE_SLL2, SIZE_SLL2
    dec SIZE_L1, SIZE

    # white
    ldi PLAYER_COLOR, 0
    not PLAYER_COLOR, PLAYER_COLOR

    # red
    ldi BALL_COLOR, 0xFF00
    ldi $t1, 0x100 # << 8
    mul BALL_COLOR, BALL_COLOR, $t1

    loop:
        j update_player
        return_update_player:

        j update_ball
        return_update_ball:

        j loop

    update_player:
        # $t1 = current pos
        # $t2 = aux
        # $t3 = next pos

        # get pos
        lw $t1, PLAYER_Y(0)

        # move
        lw $t2, PLAYER_MOVE(0)
        add $t3, $t1, $t2

        # bounds
        beq $t3, $zero, invert_player_move
        beq $t3, SIZE_L1, invert_player_move
        return_invert_player_move:

        # save position
        sw $t3, PLAYER_Y(0)

        # clear
        mul $t2, $t1, SIZE_SLL2
        sw $zero, framebuf($t2)

        # draw
        mul $t2, $t3, SIZE_SLL2
        sw PLAYER_COLOR, framebuf($t2)
        j return_update_player

    invert_player_move:
        # $t2 = player move
        not $t2, $t2
        inc $t2, $t2
        sw $t2, PLAYER_MOVE(0)
        j return_invert_player_move

    update_ball:
        # $t1 = current ball x
        # $t2 = current ball y
        # $t3 = aux x
        # $t4 = aux y
        # $t5 = next ball x
        # $t6 = next ball y

        # get pos
        lw $t1, BALL_X(0)
        lw $t2, BALL_Y(0)

        # move
        lw $t3, BALL_MOVE_X(0)
        lw $t4, BALL_MOVE_Y(0)
        add $t5, $t1, $t3
        add $t6, $t2, $t4

        # check bounds
        beq $t5, $zero, invert_ball_move_x
        beq $t5, SIZE_L1, invert_ball_move_x
        return_invert_ball_move_x:

        beq $t6, $zero, invert_ball_move_y
        beq $t6, SIZE_L1, invert_ball_move_y
        return_invert_ball_move_y:

        # save position
        sw $t5, BALL_X(0)
        sw $t6, BALL_Y(0)

        # clear
        mul $t3, $t2, SIZE
        add $t3, $t3, $t1
        sll $t3, $t3
        sll $t3, $t3
        sw $zero, framebuf($t3)

        # draw
        mul $t3, $t6, SIZE
        add $t3, $t3, $t5
        sll $t3, $t3
        sll $t3, $t3
        sw BALL_COLOR, framebuf($t3)
        j return_update_ball

    invert_ball_move_y:
        # $t4 = ball move y
        not $t4, $t4
        inc $t4, $t4
        sw $t4, BALL_MOVE_Y(0)
        j return_invert_ball_move_y

    invert_ball_move_x:
        # $t3 = ball move x
        not $t3, $t3
        inc $t3, $t3
        sw $t3, BALL_MOVE_X(0)
        j return_invert_ball_move_x
