"""
instruction.py

"""

import re
from state import ABI_TO_REGISTER_IDX

ARG_REGISTER = 1
ARG_MEMORY = 2
ARG_CONSTANT = 3

class RiscvArg():
    """
    Represents an abstract righthand side argument.
    """
    def __init__(self, arg):
        self.token = arg

        if self.is_valid_register(arg):
            self.type = ARG_REGISTER
            self.register_name = arg
            self.register_idx = ABI_TO_REGISTER_IDX[arg]
        elif self.is_memory_ref(arg):
            self.type = ARG_MEMORY
            # Parse token of the form 'offset(base)'
            offset = self.token.split('(')[0]
            base = self.token.split('(')[1].strip(')').lower()
            if self.is_valid_register(base):
                self.mem_location = offset + base
        else:
            self.type = ARG_CONSTANT

    def print(self):
        print(self.token)

    def is_valid_register(self, register):
        register = register.lower()
        if register in ABI_TO_REGISTER_IDX:
            return ABI_TO_REGISTER_IDX[register]
        else:
            return None

    def is_memory_ref(self, memory):
        return re.match(r'-{0,1}[a-z0-9]*\(([a-z0-9]*)\)', memory)

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
        self.tokens = tokens
        self.opcode = tokens[0]
        if len(tokens) > 1:
            self.args = tokens[1:]
        else:
            self.args = []

        for arg in self.args:
            arg = RiscvArg(arg)

    def print(self):
        print(self.tokens)

    # addi    arg0, arg1, arg2
    # arg0 = arg1 + sext(arg2)
    def execute_addi(self, state):
        # Technically arg2 is sign extended but doesn't matter in Python.
        arg0 = state.get_arg_val(self.args[1]) + state.get_arg_val(self.args[2])
        state.update_val(self.args[0].mem_location, arg0)

    # beq    arg0, arg1, arg2
    # jump to arg2 if arg0 == arg1
    def execute_beq(self, state, block_labels_to_lines):
        arg0 = state.get_arg_val(self.args[0])
        if block_labels_to_lines[arg0]:
            pc = block_labels_to_lines[arg0]
        else:
            pc = arg0
        if state.get_arg_val(self.args[0]) == state.get_arg_val(self.args[1]):
            state.set_register(32, pc)
        return arg0

    # bne    arg0, arg1, arg2
    # jump to arg2 if arg0 != arg1
    def execute_bne(self, state, block_labels_to_lines):
        arg0 = state.get_arg_val(self.args[0])
        if block_labels_to_lines[arg0]:
            pc = block_labels_to_lines[arg0]
        else:
            pc = arg0
        if state.get_arg_val(self.args[0]) != state.get_arg_val(self.args[1]):
            state.set_register(32, pc)
        return arg0

    # j    arg0
    # jump to arg0
    def execute_j(self, state, block_labels_to_lines):
        arg0 = state.get_arg_val(self.args[0])
        if block_labels_to_lines[arg0]:
            pc = block_labels_to_lines[arg0]
        else:
            pc = arg0
        state.set_register(32, pc)
        return arg0

    # lui    arg0, arg1
    # arg0 = arg1 << 12
    def execute_lui(self, state):
        arg0 = state.get_arg_val(self.args[1]) << 12
        state.update_val(self.args[0].mem_location, arg0)

    # lw    arg0, arg1(arg2)
    # arg0 = arg2 + arg1
    def execute_lw(self, state):
        arg0 = state.get_arg_val(self.args[2]) + state.get_arg_val(self.args[1])
        state.update_val(self.args[0].mem_location, arg0)

    def execute_ret(self, state):
        # Return address will be at top of stack.
        sp = state.get_register(2)
        state.set_register(32, sp)
        # TODO: update current_block

    # sw    arg0, arg1(arg2)
    # arg2 + arg1 = arg0
    def execute_sw(self, state):
        mem_location = state.get_arg_val(self.args[2]) + state.get_arg_val(self.args[1])
        arg0 = state.get_arg_val(self.args[0])
        state.update_val(mem_location, arg0)

    def execute(self, state, block_labels_to_lines):
        no_jump = 1
        if self.opcode == "addi":
            self.execute_addi(state)
        elif self.opcode == "beq":
            return self.execute_beq(state, block_labels_to_lines)
        elif self.opcode == "bne":
            return self.execute_bne(state, block_labels_to_lines)
        elif self.opcode == "call":
            # TODO: simulate calling function
            pass
        elif self.opcode == "j":
            return self.execute_j(self, state, block_labels_to_lines)
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
