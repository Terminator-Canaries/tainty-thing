"""
instruction.py

"""

from state import is_valid_register, ABI_TO_REGISTER_IDX

# Argument types
ARG_REGISTER = 1
ARG_MEMORY = 2
ARG_CONSTANT = 3
ARG_OTHER = 4

class RiscvArg():
    """
    Represents an abstract righthand side argument.
    """
    def __init__(self, arg):
        self.token = arg

        if is_valid_register(self.token):
            self.type = ARG_REGISTER
            self.register_name = self.token
            self.register_idx = ABI_TO_REGISTER_IDX[self.token]
        else:
            self.type = ARG_MEMORY
            # Parse token of the form '-offset(base)'
            offset = self.token.split('(')[0]
            base = self.token.split('(')[1].strip(')').lower()
            if is_valid_register(base):
                self.mem_location = offset + base

    def print(self):
        print(self.token)

    def is_register(self):
        return self.type == ARG_REGISTER

    def is_memory(self):
        return self.type == ARG_MEMORY


class RiscvInstr():
    """
    Represents a single line of RISC-V binary.
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.opcode = tokens[0]
        if len(tokens) > 1:
            self.args = tokens[1:]

        for arg in self.args:
            arg = RiscvArg(arg)

    def print(self):
        print(self.tokens)

    # addi    arg0, arg1, arg2
    def execute_addi(self, state):
        # Technically arg2 is sign extended but doesn't matter in Python.
        arg0 = state.get_arg_val(self.args[1]) + state.get_arg_val(self.args[2])
        state.update_val(args[0], arg0)

    # lui    arg0, arg1
    def execute_lui(self, state):
        arg0 = state.get_arg_val(args[1]) << 12
        state.update_val(args[0], arg0)

    # lw    arg0, arg1(arg2)
    def execute_lw(self, state):
        return args[1] + sext(args[2])

    # sw    arg0, arg1(arg2)
    def execute_sw(self, state):
        return args[0]

    def execute(self, state):
        if self.opcode == "addi":
            execute_addi(self.args)
        elif self.opcode == "beq":
            if execute_beq(args):

        elif self.opcode == "bne":
            if execute_bne(args):

        elif self.opcode == "call":
            call_func = args[0]
            # TODO: call function
        elif self.opcode == "j":
            jump_target = args[0]
            jump_block = blocks[jump_target]
            self.current_block = jump_block
        elif self.opcode == "lui":
            self.execute_lui(self.args)
        elif self.opcode == "lw":
            update_val = execute_lw(args)
            update_state(instr.args[0])
        elif self.opcode == "sw":
            # TODO: figure out how to reverse 'lw'
        else:
            return None

