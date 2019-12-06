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

        self.base = base
        if offset[0] == '-':
            self.offset = -int(offset[1:])
        else:
            self.offset = int(offset)
        self.offset = offset

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

        if self.is_valid_register(self._token) is not None:
            self.type = OPERAND_REGISTER
            self.register_name = self._token
            self.register_idx = ABI_TO_REGISTER_IDX[self._token]
        elif self.is_memory_ref():
            self.type = OPERAND_MEMORY
            self.mem_reference = MemoryReference(token)
        else:
            self.type = OPERAND_CONSTANT
            self.constant = int(self._token)

    def to_string(self):
        return str(self._token)

    # Check if string is a valid ABI register name.
    def is_valid_register(self, val):
        register = val.lower()
        if register in ABI_TO_REGISTER_IDX:
            return ABI_TO_REGISTER_IDX[register]
        else:
            return None

    # Check if int is a valid memory address.
    def is_valid_memory(self, val):
        return int(val) >= 0 and int(val) < 4096

    # Check if string matches pattern 'offset(base)'.
    def is_memory_ref(self):
        return re.match(r'-{0,1}[a-z0-9]*\(([a-z0-9]*)\)', self._token)

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

    def get_jump_target(self, target, lines):
        # Jump target is a block label.
        if lines[target] is not None:
            pc = lines[target]
        # Jump target is a line number.
        else:
            pc = target
            raise Exception("Jump target is not a block label")
        return pc

    def generate_mem_operand(self, operand, state):
        # Calculate int memory address.
        base = RiscvOperand(operand.mem_reference.get_base())
        offset = RiscvOperand(operand.mem_reference.get_offset())
        mem_location = state.get_operand_val(base) + state.get_operand_val(offset)
        # Create operand representing the address mem_location using format 'offset(base)'.
        mem_reference = RiscvOperand(str(mem_location) + "(zero)")
        return mem_reference

    # addi    op0, op1, op2
    # op0 = op1 + sext(op2)
    def execute_addi(self, state):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        # Technically op2 is sign extended but doesn't matter in Python.
        val1 = state.get_operand_val(self.operands[1])
        val2 = state.get_operand_val(self.operands[2])
        update_val = val1 + val2
        state.update_val(self.operands[0], update_val)

    # subi    op0, op1, op2
    # op0 = op1 - sext(op2)
    def execute_subi(self, state):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        # Technically op2 is sign extended but doesn't matter in Python.
        val1 = state.get_operand_val(self.operands[1])
        val2 = state.get_operand_val(self.operands[2])
        update_val = val1 - val2
        state.update_val(self.operands[0], update_val)

    # beq    op0, op1, op2
    # jump to op2 if op0 == op1
    def execute_beq(self, state, lines):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        branch_val = state.get_operand_val(self.operands[0])
        pc = self.get_jump_target(branch_val, lines)
        if state.get_operand_val(self.operands[0]) == state.get_operand_val(self.operands[1]):
            state.set_register(32, pc)
        return branch_val

    # bne    op0, op1, op2
    # jump to op2 if op0 != op1
    def execute_bne(self, state, lines):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        branch_val = state.get_operand_val(self.operands[0])
        pc = self.get_jump_target(branch_val, lines)
        if state.get_operand_val(self.operands[0]) != state.get_operand_val(self.operands[1]):
            state.set_register(32, pc)
        return branch_val

    # j    op0
    # jump to op0
    def execute_j(self, state, lines):
        if len(self.operands) < 1:
            raise InsufficientOperands()
        jump_val = state.get_operand_val(self.operands[0])
        pc = self.get_jump_target(jump_val, lines)
        state.set_register(32, pc)
        return jump_val

    # lui    op0, op1
    # op0 = op1 << 12
    def execute_lui(self, state):
        if len(self.operands) < 2:
            raise InsufficientOperands()
        update_val = state.get_operand_val(self.operands[1]) << 12
        state.update_val(self.operands[0], update_val)

    # lw    op0, op1(op2)
    # op0 = val(op2 + op1)
    def execute_lw(self, state):
        if len(self.operands) < 2:
            raise InsufficientOperands()
        mem_reference = self.generate_mem_operand(self.operands[1], state)
        load_val = state.get_operand_val(mem_reference)
        state.update_val(self.operands[0], load_val)

    def execute_ret(self, state):
        if len(self.operands) != 0:
            raise InsufficientOperands()
        # Return address is stored in 'ra'.
        ra = state.get_register(1)
        state.set_register(32, ra)
        # TODO: update current_block

    # sw    op0, op1(op2)
    # val(op2 + op1) = op0
    def execute_sw(self, state):
        if len(self.operands) < 2:
            raise InsufficientOperands()
        mem_reference = self.generate_mem_operand(self.operands[1], state)
        store_val = state.get_operand_val(self.operands[0])
        state.update_val(mem_reference, store_val)

    def execute(self, state, lines):
        no_jump = 1
        if self.opcode == "addi" or self.opcode == "add":
            self.execute_addi(state)
        elif self.opcode == "subi" or self.opcode == "sub":
            self.execute_subi(state)
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
