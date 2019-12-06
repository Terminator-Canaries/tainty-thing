"""
instruction.py

"""

import re
from state import ABI_TO_REGISTER_IDX

OPERAND_REGISTER = 1
OPERAND_MEMORY = 2
OPERAND_CONSTANT = 3


class InsufficientOperands(Exception):
    """
    Raise when execute_opcode called with insufficent operands.
    """
    pass


class MemoryReference():
    """
    Necessary so that resolving reference is done only upon excuting.
    """
    def __init__(self, token):
        base = token.split('(')[1].strip(')').lower()
        offset = token.split('(')[0]

        if offset[0] == '-':
            self.offset = -int(offset[1:])
        else:
            self.offset = int(offset)
        self.offset = offset

        self.base = base
        self.mem_location = -1

    def get_offset(self):
        return self.offset

    def get_base(self):
        return self.base


class RiscvOperand():
    """
    Represents an abstract righthand side operand.
    """
    def __init__(self, token):
        self._token = token
        self._offset = 0

        if self.is_valid_register(self._token):
            self.type = OPERAND_REGISTER
            self.register_name = self._token
            self.register_idx = ABI_TO_REGISTER_IDX[self._token]
        elif self.is_memory_ref():
            self.type = OPERAND_MEMORY
            self.mem_reference = MemoryReference(token)
        else:
            self.type = OPERAND_CONSTANT
            self.constant = int(token)

    def to_string(self):
        return str(self._token)

    def is_valid_register(self, register):
        return register.lower() in ABI_TO_REGISTER_IDX

    def is_memory_ref(self):
        return re.match(r'-{0,1}[a-z0-9]*\(([a-z0-9]*)\)', self._token)

    def is_valid_register(self, register):
        register = register.lower()
        if register in ABI_TO_REGISTER_IDX:
            return ABI_TO_REGISTER_IDX[register]
        else:
            return None

    def is_memory_ref(self, memory):
        return re.match(r'-{0,1}[a-z0-9]*\(([a-z0-9]*)\)', memory)

    def is_register(self):
        return self.type == OPERAND_REGISTER

    def is_memory(self):
        return self.type == OPERAND_MEMORY

    def is_constant(self):
        return self.type == OPERAND_CONSTANT


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

    # addi    op0, op1, op2
    # op0 = op1 + sext(op2)
    def execute_addi(self, state):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        # Technically op2 is sign extended but doesn't matter in Python.
        val1 = state.get_operand_val(self.operands[1])
        val2 = state.get_operand_val(self.operands[2])
        print(val1, val2)
        print(type(val1), type(val2))
        op0 = val1 + val2
        state.update(self.operands[0].mem_location, op0)

    # beq    op0, op1, op2
    # jump to op2 if op0 == op1
    def execute_beq(self, state, lines):
        op0 = state.get_operand_val(self.operands[0])
        if lines[op0]:
            pc = lines[op0]
        else:
            pc = op0
        if state.get_operand_val(self.operands[0]) == state.get_operand_val(self.operands[1]):
            state.set_register(32, pc)
        return op0

    # bne    op0, op1, op2
    # jump to op2 if op0 != op1
    def execute_bne(self, state, lines):
        op0 = state.get_operand_val(self.operands[0])
        if lines[op0]:
            pc = lines[op0]
        else:
            pc = op0
        if state.get_operand_val(self.operands[0]) != state.get_operand_val(self.operands[1]):
            state.set_register(32, pc)
        return op0

    # j    op0
    # jump to op0
    def execute_j(self, state, lines):
        op0 = state.get_operand_val(self.operands[0])
        if lines[op0]:
            pc = lines[op0]
        else:
            pc = op0
        state.set_register(32, pc)
        return op0

    # lui    op0, op1
    # op0 = op1 << 12
    def execute_lui(self, state):
        op0 = state.get_operand_val(self.operands[1]) << 12
        state.update_val(self.operands[0].mem_location, op0)

    # lw    op0, op1(op2)
    # op0 = op2 + op1
    def execute_lw(self, state):
        op0 = state.get_operand_val(self.operands[2]) + state.get_operand_val(self.operands[1])
        state.update_val(self.operands[0].mem_location, op0)

    def execute_ret(self, state):
        # Return address will be at top of stack.
        sp = state.get_register(2)
        state.set_register(32, sp)
        # TODO: update current_block

    # sw    op0, op1(op2)
    # op2 + op1 = op0
    def execute_sw(self, state):
        mem_location = state.get_operand_val(self.operands[2]) + state.get_operand_val(self.operands[1])
        op0 = state.get_operand_val(self.operands[0])
        state.update_val(mem_location, op0)

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
            return self.execute_j(state, lines)
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
