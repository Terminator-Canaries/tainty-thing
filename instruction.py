"""
instruction.py

"""

import re
from state import ABI_TO_REGISTER_IDX

ARG_REGISTER = 1
ARG_MEMORY = 2
ARG_CONSTANT = 3


class InsufficientOperands(Exception):
    """
    Raise when execute_opcode called with insufficent operands.
    """
    pass


class RiscvOperand():
    """
    Represents an abstract righthand side argument.
    """
    def __init__(self, token):
        self._token = token
        self._offset = 0

        if self.is_valid_register(self._token):
            self.type = ARG_REGISTER
            self.register_name = self._token
            self.register_idx = ABI_TO_REGISTER_IDX[self._token]
        elif self.is_memory_ref():
            self.type = ARG_MEMORY
            # Parse token of the form 'offset(base)'
            offset = self._token.split('(')[0]
            if offset[0] == '-':
                self.offset = -int(offset[1:])
            else:
                self.offset = int(offset)
            base = self._token.split('(')[1].strip(')').lower()
            if self.is_valid_register(base):
                self.mem_location = self.offset + base
        else:
            self.type = ARG_CONSTANT

    def to_string(self):
        return str(self._token)

    def is_valid_register(self, register):
        return register.lower() in ABI_TO_REGISTER_IDX

    def is_memory_ref(self):
        return re.match(r'-{0,1}[a-z0-9]*\(([a-z0-9]*)\)', self._token)

    def is_register(self):
        return self.type == ARG_REGISTER

    def is_memory(self):
        return self.type == ARG_MEMORY

    def is_constant(self):
        return self.type == ARG_CONSTANT


class RiscvInstr():
    """
    Represents a single line of RISC-V binary.
    """
    def __init__(self, tokens):
        self._tokens = tokens
        self.opcode = tokens[0]
        self.operands = []

        if len(tokens) > 1:
            self.operands = [RiscvOperand(operand) for operand in tokens[1:]]

    def to_string(self):
        return str(self._tokens)

    # addi    arg0, arg1, arg2
    # arg0 = arg1 + sext(arg2)
    def execute_addi(self, state):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        # Technically arg2 is sign extended but doesn't matter in Python.
        val1 = state.get_arg_val(self.operands[1])
        val2 = state.get_arg_val(self.operands[2])
        print(val1, val2)
        print(type(val1), type(val2))
        arg0 = val1 + val2
        state.update(self.operands[0].mem_location, arg0)

    # beq    arg0, arg1, arg2
    # jump to arg2 if arg0 == arg1
    def execute_beq(self, state, lines):
        arg0 = state.get_arg_val(self.operands[0])
        if lines[arg0]:
            pc = lines[arg0]
        else:
            pc = arg0
        if state.get_arg_val(self.operands[0]) == state.get_arg_val(self.operands[1]):
            state.set_register(32, pc)
        return arg0

    # bne    arg0, arg1, arg2
    # jump to arg2 if arg0 != arg1
    def execute_bne(self, state, lines):
        arg0 = state.get_arg_val(self.operands[0])
        if lines[arg0]:
            pc = lines[arg0]
        else:
            pc = arg0
        if state.get_arg_val(self.operands[0]) != state.get_arg_val(self.operands[1]):
            state.set_register(32, pc)
        return arg0

    # j    arg0
    # jump to arg0
    def execute_j(self, state, lines):
        arg0 = state.get_arg_val(self.operands[0])
        if lines[arg0]:
            pc = lines[arg0]
        else:
            pc = arg0
        state.set_register(32, pc)
        return arg0

    # lui    arg0, arg1
    # arg0 = arg1 << 12
    def execute_lui(self, state):
        arg0 = state.get_arg_val(self.operands[1]) << 12
        state.update_val(self.operands[0].mem_location, arg0)

    # lw    arg0, arg1(arg2)
    # arg0 = arg2 + arg1
    def execute_lw(self, state):
        arg0 = state.get_arg_val(self.operands[2]) + state.get_arg_val(self.operands[1])
        state.update_val(self.operands[0].mem_location, arg0)

    def execute_ret(self, state):
        # Return address will be at top of stack.
        sp = state.get_register(2)
        state.set_register(32, sp)
        # TODO: update current_block

    # sw    arg0, arg1(arg2)
    # arg2 + arg1 = arg0
    def execute_sw(self, state):
        mem_location = state.get_arg_val(self.operands[2]) + state.get_arg_val(self.operands[1])
        arg0 = state.get_arg_val(self.operands[0])
        state.update_val(mem_location, arg0)

    def execute(self, state, lines):
        no_jump = 1
        if self.opcode == "addi":
            self.execute_addi(state)
        elif self.opcode == "beq":
            return self.execute_beq(state, lines)
        elif self.opcode == "bne":
            return self.execute_bne(state, lines)
        elif self.opcode == "call":
            # TODO: simulate calling function
            pass
        elif self.opcode == "j":
            return self.execute_j(self, state, lines)
        elif self.opcode == "lui":
            self.execute_lui(state)
        elif self.opcode == "lw":
            self.execute_lw(state)
        elif self.opcode == "ret":
            self.execute_ret(state)
            return 0
        elif self.opcode == "sw":
            self.execute_sw(state)
        else:
            return None
        return no_jump
