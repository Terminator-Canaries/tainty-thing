"""
instruction.py

Defines an object representation for RISC-V instructions.
"""

from state import is_valid_register, ABI_TO_REGISTER_IDX

# Argument types
ARG_REGISTER = 1
ARG_MEMORY = 2
ARG_CONSTANT = 3


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

    def print_arg(self):
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
        self.args = tokens[1:]

        for arg in self.args:
            arg = RiscvArg(arg)

    def print_instr(self):
        print(self.tokens)
