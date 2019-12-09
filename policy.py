#!/usr/bin/env python3
from instruction import SUPPORTED_FUNCTIONS
from functools import partial

## TAINT POLICY HANDLERS ##
# A taint handler is function of arguments (tracker, state, operands).
#   tracker: instantiated taint tracker
#   state: execution state
#   operands: operands to the operation


# addi    op0, op1, op2
# op0 = op1 + sext(op2)
def taint_addi(tracker, state, operands):
    taint1 = tracker.get_operand_taint(operands[1])
    taint2 = tracker.get_operand_taint(operands[2])
    print("Taint1 {} taint2 {}".format(taint1,taint2))
    print(tracker.OR(taint1, taint2))
    tracker.replace_operand_taint(operands[0], tracker.OR(taint1, taint2))


# sw    op0, op1(op2)
# val(op2 + op1) <- op0
def taint_sw(tracker, state, operands):
    taint1 = tracker.get_operand_taint(operands[0])
    tracker.replace_operand_taint(operands[1], taint1)


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
    tracker.replace_operand_taint(operands[0], taint1)


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
    print(function_name)
    if function_name in SUPPORTED_FUNCTIONS:
        print("############CALL")
        tracker.taint_source = SUPPORTED_FUNCTIONS[function_name]
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

def pc_wrapper(handler, tracker, state, operands):
    pc = state.get_register('pc')
    if  pc > 14 and pc < 18:
        tracker.print_registers_taint()
    handler(tracker, state,operands)

# A policy is a mapping of instruction string labels to their handlers.
policy = {
    "addi": partial(pc_wrapper, handler=taint_addi),
    "add": partial(pc_wrapper, handler=taint_addi),
    "sw": taint_sw,
    "call": taint_call,
    "mv": taint_mv,
    "ret": taint_ret,
    "lw": taint_lw,
    "blt": thunk,
    "bne": thunk,
    "beq": thunk,
    "j": thunk,
    "jalr": thunk,
    "lui": taint_lui
}
