"""
instruction.py

Defines an object representation for RISC-V instructions.
"""

from state import *


ARG_REGISTER = 1
ARG_MEMORY = 2
ARG_OTHER = 3

# Represents an abstrat righthand side argument.
class RiscvArg():
	def __init__(self, token):
    	self.token = token

    	if isValidRegister(self.token):
    		self.type = ARG_REGISTER
    		self.register_name = self.token
    		self.register_idx = ABI_TO_REGISTER_IDX[self.token]
    	else:
    		self.type = ARG_MEMORY
    		# Parse token of the form '-offset(base)'
    		offset = self.token.split('(')[0]
    		base = self.token.split('(')[1].strip(')')
    		if isValidRegister(base):
    			self.mem_location = offset + base

    def printArg():
    	print(self.token)


# Represents a single line of a RISC-V binary.
class RiscvInstr():
    def __init__(self, tokens):
    	self.tokens = tokens
    	self.opcode = tokens[0]

        self.args = tokens[1:]
        for arg in self.args:
        	arg = RiscvArg(arg)

    def printInstr():
    	print(self.tokens)
