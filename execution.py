"""
executions.py

Defines functions that execute most common RISC instructions.
To support a new instruction add its corresponding function here.
All functions must take an array of argument to simulate passing
by reference.
"""

## Arithmetic operations

# addi    arg0, arg1, arg2
execute_addi(args):
	return args[1] + sext(args[2])

# lui    arg0, arg1
execute_lui(args):
	return args[1] << 12

# lw    arg0, arg1(arg2)
execute_lw(args):
	return args[1] + sext(args[2])

# sw    arg0, arg1(arg2)
execute_sw(args):
	return args[0]


## Conditional breaks

# beq    arg0, arg1
execute_beq(args):
	return args[0] == args[1]

# bne    arg0, arg1
execute_bne(args):
	return args[0] != args[1]


## Calls and jumps

# call    arg0
execute_call(args):
	return args[0]

# j    arg0
execute_j(args):
	return args[0]
