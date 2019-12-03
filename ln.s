	.text
	.file	"testprogram.c"
	.globl	main                    # -- Begin function main
	.p2align	2
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:
	addi	sp, sp, -32
	.cfi_def_cfa_offset 32
	sw	ra, 28(sp)
	sw	s0, 24(sp)
	.cfi_offset ra, -4
	.cfi_offset s0, -8
	addi	s0, sp, 32
	.cfi_def_cfa s0, 0
	sw	zero, -12(s0)
	sw	a0, -16(s0)
	sw	a1, -24(s0)
	lw	a1, -16(s0)
	addi	a0, zero, 3
	beq	a1, a0, .LBB0_2
	j	.LBB0_1
.LBB0_1:
	addi	a0, zero, 1
	sw	a0, -12(s0)
	j	.LBB0_5
.LBB0_2:
	lui	a0, %hi(.L.str)
	addi	a0, a0, %lo(.L.str)
	call	printf
	lw	a0, -24(s0)
	lw	a0, 4(a0)
	call	atoi
	sw	a0, -28(s0)
	lw	a0, -24(s0)
	lw	a0, 8(a0)
	call	atoi
	sw	a0, -32(s0)
	lw	a1, -28(s0)
	addi	a0, zero, 1
	bne	a1, a0, .LBB0_4
	j	.LBB0_3
.LBB0_3:
	lw	a1, -28(s0)
	lw	a0, -32(s0)
	add	a0, a1, a0
	sw	a0, -12(s0)
	j	.LBB0_5
.LBB0_4:
	sw	zero, -12(s0)
	j	.LBB0_5
.LBB0_5:
	lw	a0, -12(s0)
	lw	s0, 24(sp)
	.cfi_def_cfa sp, 32
	lw	ra, 28(sp)
	.cfi_restore ra
	.cfi_restore s0
	addi	sp, sp, 32
	.cfi_def_cfa_offset 0
	ret
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc
                                        # -- End function
	.type	.L.str,@object          # @.str
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str:
	.asciz	"hi\n"
	.size	.L.str, 4


	.ident	"Apple clang version 11.0.0 (clang-1100.0.33.12)"
	.section	".note.GNU-stack","",@progbits
