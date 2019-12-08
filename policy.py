#!/usr/bin/env python3
from instruction import SUPPORTED_FUNCTIONS

## BEGIN HANDLERS ##
# a taint handler is function of arguments (tracker, state, operands)
# where tracker is the instantiated taint tracker, state is the execution state and operands
# is the operands to the operation


# addi    op0, op1, op2
# op0 = op1 + sext(op2)
def taint_addi(tracker, state, operands):
    taint1 = tracker.get_operand_taint(operands[1])
    taint2 = tracker.get_operand_taint(operands[2])
    tracker.replace_operand_taint(operands[0], tracker.OR(taint1, taint2))


# sw    op0, op1(op2)
# val(op2 + op1) <- op0
def taint_sw(tracker, state, operands):
    taint1 = tracker.get_operand_taint(operands[0])
    tracker.replace_operand_taint(operands[1], taint1)


# addi    op0, op1, op2
# op0 = op1 + sext(op2)
def taint_addi(tracker, state, operands):
    taint1 = tracker.get_operand_taint(operands[1])
    taint2 = tracker.get_operand_taint(operands[2])
    tracker.replace_operand_taint(operands[0], tracker.OR(taint1, taint2))


# subi    op0, op1, op2
# op0 = op1 - sext(op2)
def taint_subi(tracker, state, operands):
    taint1 = tracker.get_operand_taint(operands[1])
    taint2 = tracker.get_operand_taint(operands[2])
    tracker.replace_operand_taint(operands[0], tracker.OR(taint1, taint2))


# beq    op0, op1, op2
# jump to op2 if op0 == op1
def taint_beq(tracker, state, operands):
    # TODO - Jump tainting
    return


# bne    op0, op1, op2
# jump to op2 if op0 != op1
def taint_bne(tracker, state, operands):
    # TODO - Jump tainting
    return


# j    op0
# jump to op0
def taint_j(tracker, state, operands):
    # TODO - Jump tainting
    return


# lui    op0, op1
# op0 = op1 << 12
def taint_lui(tracker, state, operands):
    taint1 = tracker.get_operand_taint(operands[1])
    self.replace_operand_taint(operands[0], taint1)


# lw    op0, op1(op2)
# op0 = val(op2 + op1)
def taint_lw(tracker, state, operands):
    taint1 = tracker.get_operand_taint(operands[1])
    tracker.replace_operand_taint(operands[0], taint1)


def taint_ret(tracker, state, operands):
    # Return address is stored in 'ra'.
    if tracker.taint_source != 0:
        tracker.replace_register_taint("a0", tracker.taint_source)
    tracker.taint_source = 0
    return


# call   op0
# taint function op0
def taint_call(tracker, state, operands):
    function_name = operands[0].get_target_name()
    if function_name in SUPPORTED_FUNCTIONS:
        tracker.taint_source = SUPPORTED_FUNCTIONS[function_name]
    else:
        raise Exception("Function {} not taint call supported.".format(function_name))
    return


def taint_mv(tracker, state, operands):
    taint2 = tracker.get_operand_taint(operands[1])
    tracker.replace_operand_taint(operands[0], taint2)
    return


def thunk(tracker, state, operands):
    pass


# lw op0, op1(op2)
# op0 = val(op2 + op1)
def taint_lw(tracker, state, operands):
    ## TODO:!!! this is not an ideal implementation,
    ## but control flow taint is doable from here
    # if either of the values are tainted,
    # propagate that taint to the result
    # op1 = operands[1].mem_reference.get_base()
    # op2 = operands[1].mem_reference.get_offset()
    # tracker.get_operand_taint(o)
    # otherwise
    mem_taint = tracker.get_operand_taint(operands[1])
    tracker.replace_operand_taint(operands[0], mem_taint)
    return


## BEGIN POLICY ##
# A policy is a mapping of instruction string labels to their handlers
policy = {
    "addi": taint_addi,
    "add": taint_addi,
    "sw": taint_sw,
    "call": taint_call,
    "mv": taint_mv,
    "ret": taint_ret,
    "lw": taint_lw,
    "blt": thunk,
    "bne": thunk,
    "beq": thunk,
    "j": thunk,
}

# # Handle the specified operation.
# elif opcode == "subi" or opcode == "sub":
#     return self.taint_subi(opcode, operands)
# elif opcode == "beq":
#     return self.taint_beq(opcode, operands)
# elif opcode == "bne":
#     return self.taint_bne(opcode, operands)
# elif opcode == "j":
#     return self.taint_j(opcode, operands)
# elif opcode == "lui":
#     return self.taint_lui(opcode, operands)
# elif opcode == "lw":
#     return self.taint_lw(opcode, operands)
# else:
