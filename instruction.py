"""
instruction.py

Defines an object representation for RISC-V instructions.
* class RiscvInstr - Parses tokens and creates an object for executing instructions.
* class RiscvOperand - Represents an abstract righthand side operand.
Stores information relevant to classifying operand types (mem refs, consts, regs).
* class MemoryReference - Abstraction for representing mem reference operands. 
"""

import re
from state import ABI_TO_REGISTER_IDX

OPERAND_REGISTER = 1
OPERAND_MEMORY = 2
OPERAND_CONSTANT = 3
OPERAND_LABEL = 4
OPERAND_CALL_FUNCTION = 5

# Taint Flags
# If flags change, edit function tracker.get_taint_as_string().
TAINT_LOC = 0x1
TAINT_UID = 0x10
TAINT_NAME = 0x100
TAINT_FACE = 0x1000
TAINT_PASSWORD = 0x10000
TAINT_OTHER = 0x100000

SUPPORTED_FUNCTIONS = {
    "get_user_location": TAINT_LOC,
    "get_uid": TAINT_UID,
    "get_user_name": TAINT_NAME,
    "get_face": TAINT_FACE,
    "get_password": TAINT_PASSWORD,
}


class InsufficientOperands(Exception):
    """
    Raise when execute_opcode called with insufficent operands.
    """
    pass


class MemoryReference:
    """
    Necessary so that resolving reference is done only upon excuting.
    """
    def __init__(self, token):
        base = token.split("(")[1].strip(")").lower()
        offset = token.split("(")[0]

        self.base = base
        if offset[0] == "-":
            self.offset = -int(offset[1:])
        else:
            self.offset = int(offset)
        self.offset = offset

    def get_offset(self):
        return self.offset

    def get_base(self):
        return self.base


class RiscvOperand:
    """
    Represents an abstract righthand side operand.
    """
    def __init__(self, token, block_labels):
        self._token = token
        self._offset = 0

        if self._token in ABI_TO_REGISTER_IDX:
            self._type = OPERAND_REGISTER
            self.register_name = self._token
            self.register_idx = ABI_TO_REGISTER_IDX[self._token]
        elif self._token in block_labels:
            self._type = OPERAND_LABEL
            self.target_line = block_labels[self._token]
        elif self._is_memory_ref():
            self._type = OPERAND_MEMORY
            self.mem_reference = MemoryReference(token)
        elif self.is_call_function():
            self.type = OPERAND_CALL_FUNCTION
            self.constant = str(self._token)
        else:
            self._type = OPERAND_CONSTANT
            self.constant = int(self._token)

    def to_string(self):
        return str(self._token)

    # Check if string matches pattern 'offset(base)'.
    def _is_memory_ref(self):
        return re.match(r"-{0,1}[a-z0-9]*\(([a-z0-9]*)\)", self._token)

    # Check if the token is a supported function.
    def is_call_function(self):
        return self._token in SUPPORTED_FUNCTIONS

    def is_register(self):
        return self._type == OPERAND_REGISTER

    def is_memory(self):
        return self._type == OPERAND_MEMORY

    def is_constant(self):
        return self._type == OPERAND_CONSTANT

    def is_label(self):
        return self._type == OPERAND_LABEL

    def get_target_name(self):
        if self._type != OPERAND_LABEL:
            raise Exception(
                "Target {} is not an operand label.".format(self.to_string())
            )
        return self._token


class RiscvInstr:
    """
    Represents a single line of RISC-V binary.
    """
    def __init__(self, tokens, block_labels):
        self._tokens = tokens
        self._block_labels = block_labels
        self.opcode = tokens[0]
        self.operands = []
        if len(tokens) > 1:
            self.operands = [
                RiscvOperand(operand, self._block_labels) for operand in tokens[1:]
            ]

    def to_string(self):
        return str(self._tokens)

    def get_jump_target(self, target):
        # Jump target is a block label.
        if self._block_labels[target] is not None:
            pc = self._block_labels[target]
        # Jump target is a line number.
        else:
            raise Exception("Jump target is not a block label")
        return pc

    def generate_mem_operand(self, operand, state):
        # Calculate int memory address.
        base = RiscvOperand(operand.mem_reference.get_base(), self._block_labels)
        offset = RiscvOperand(operand.mem_reference.get_offset(), self._block_labels)
        mem_location = state.get_operand_val(base) + state.get_operand_val(offset)
        # Create operand representing the address mem_location using format 'offset(base)'.
        mem_reference = RiscvOperand(str(mem_location) + "(zero)", self._block_labels)
        return mem_reference

    ## ARITHMETIC

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

    # andi    op0, op1, op2
    # op0 = op1 - sext(op2)
    def execute_andi(self, state):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        # Technically op2 is sign extended but doesn't matter in Python.
        val1 = state.get_operand_val(self.operands[1])
        val2 = state.get_operand_val(self.operands[2])
        update_val = val1 & val2
        state.update_val(self.operands[0], update_val)

    # xori    op0, op1, op2
    # op0 = op1 - sext(op2)
    def execute_xori(self, state):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        # Technically op2 is sign extended but doesn't matter in Python.
        val1 = state.get_operand_val(self.operands[1])
        val2 = state.get_operand_val(self.operands[2])
        update_val = val1 ^ val2
        state.update_val(self.operands[0], update_val)

    # srli    op0, op1, op2
    # op0 = op1 >> sext(op2)
    def execute_srli(self, state):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        # Technically op2 is sign extended but doesn't matter in Python.
        val1 = state.get_operand_val(self.operands[1])
        val2 = state.get_operand_val(self.operands[2])
        update_val = val1 >> val2
        state.update_val(self.operands[0], update_val)

    # slli    op0, op1, op2
    # op0 = op1 << sext(op2)
    def execute_slli(self, state):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        # Technically op2 is sign extended but doesn't matter in Python.
        val1 = state.get_operand_val(self.operands[1])
        val2 = state.get_operand_val(self.operands[2])
        update_val = val1 << val2
        state.update_val(self.operands[0], update_val)

    # lui    op0, op1
    # op0 = op1 << 12
    def execute_lui(self, state):
        if len(self.operands) < 2:
            raise InsufficientOperands()
        update_val = state.get_operand_val(self.operands[1]) << 12
        state.update_val(self.operands[0], update_val)

    ## BRANCHES

    # beq    op0, op1, op2
    # jump to op2 if op0 == op1
    def execute_beq(self, state):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        branch_val = (self.operands[2]).get_target_name()
        pc = self.get_jump_target(branch_val)
        if state.get_operand_val(self.operands[0]) == state.get_operand_val(
            self.operands[1]
        ):
            state.set_register("pc", pc)
            return branch_val
        else:
            return 1  # no_jump

    # bne    op0, op1, op2
    # jump to op2 if op0 != op1
    def execute_bne(self, state):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        branch_val = (self.operands[2]).get_target_name()
        pc = self.get_jump_target(branch_val)
        if state.get_operand_val(self.operands[0]) != state.get_operand_val(
            self.operands[1]
        ):
            state.set_register("pc", pc)
            return branch_val
        else:
            return 1  # no_jump

    # bnez    op0, op1
    # jump to op1 if op0 != 0
    def execute_bnez(self, state):
        if len(self.operands) != 2:
            raise InsufficientOperands()
        branch_val = (self.operands[1]).get_target_name()
        pc = self.get_jump_target(branch_val)
        if state.get_operand_val(self.operands[0]) != 0:
            state.set_register("pc", pc)
            return branch_val
        else:
            return 1  # no_jump

    # blt    op0, op1, op2
    # jump to op2 if op0 < op1
    def execute_blt(self, state):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        branch_val = (self.operands[2]).get_target_name()
        pc = self.get_jump_target(branch_val)
        print("pc = ", pc)
        if state.get_operand_val(self.operands[0]) < state.get_operand_val(
            self.operands[1]
        ):
            state.set_register("pc", pc)
            return branch_val
        else:
            return 1  # no_jump

    ## MEMORY

    # mv    op0, op1
    # assign op1 to op0
    def execute_mv(self, state):
        # mv is a pseudoinstruction for:
        # addi    arg1, arg2, 0
        self.operands.append(RiscvOperand("0", self._block_labels))
        self.execute_addi(state)

    # lw    op0, op1(op2)
    # op0 = val(op2 + op1)
    def execute_lw(self, state):
        if len(self.operands) < 2:
            raise InsufficientOperands()
        mem_reference = self.generate_mem_operand(self.operands[1], state)
        load_val = state.get_operand_val(mem_reference)
        state.update_val(self.operands[0], load_val)

    # sw    op0, op1(op2)
    # val(op2 + op1) = op0
    def execute_sw(self, state):
        if len(self.operands) < 2:
            raise InsufficientOperands()
        mem_reference = self.generate_mem_operand(self.operands[1], state)
        store_val = state.get_operand_val(self.operands[0])
        state.update_val(mem_reference, store_val)

    ## CALL, JUMPS, RET

    # call   op0
    # execute function op0
    def execute_call(self, state):
        if len(self.operands) < 1:
            raise InsufficientOperands()
        elif len(self.operands) != 1:
            raise Exception("Function args not yet handled")
        # Set the return address to one after the current line.
        pc = state.get_register("pc")
        state.set_register("ra", pc+1)
        # Jump to the function name.
        jump_val = (self.operands[0]).get_target_name()
        pc = self.get_jump_target(jump_val)
        state.set_register("pc", pc)
        return jump_val

    # j    op0
    # jump to op0
    def execute_j(self, state):
        if len(self.operands) < 1:
            raise InsufficientOperands()
        jump_val = (self.operands[0]).get_target_name()
        pc = self.get_jump_target(jump_val)
        state.set_register("pc", pc)
        return jump_val

    # jalr    op0, op1, op2
    # jump to (op1 + op2) with last bit 0
    # set op0 to address following the jump (%pc + 4)
    def execute_jalr(self, state):
        if len(self.operands) != 3:
            raise InsufficientOperands()
        pc = state.get_register("pc")
        # %pc = (op1 + op2) & 0xFFFFFFFE
        val1 = state.get_operand_val(self.operands[1])
        val2 = state.get_operand_val(self.operands[2])
        jump_val = val1 + val2
        state.set_register("pc", jump_val)
        # %rd = (prior %pc + 4)
        state.set_register(self.operands[0].to_string(), pc+1)
        return jump_val

    def execute_ret(self, state):
        if len(self.operands) != 0:
            print("Ret got {} operands".format([s.to_string() for s in self.operands]))
            raise InsufficientOperands()
        # ret is a pseudoinstruction for:
        # jalr    zero, ra, zero
        self.opcode = "jalr"
        self.operands = [
            RiscvOperand("zero", self._block_labels),
            RiscvOperand("ra", self._block_labels),
            RiscvOperand("zero", self._block_labels),
        ]
        # If return address is -1 then final return was executed.
        return -1 if self.execute_jalr(state) == -1 else 0

    def execute(self, state, tracker):
        result = 1
        tracker.taint_by_operand(state, self.opcode, self.operands)

        if self.opcode == "addi" or self.opcode == "add":
            self.execute_addi(state)
        elif self.opcode == "subi" or self.opcode == "sub":
            self.execute_subi(state)
        elif self.opcode == "andi" or self.opcode == "and":
            self.execute_andi(state)
        elif self.opcode == "xori" or self.opcode == "xor":
            self.execute_xori(state)
        elif self.opcode == "srli" or self.opcode == "srl":
            self.execute_srli(state)
        elif self.opcode == "slli" or self.opcode == "sll":
            self.execute_slli(state)
        elif self.opcode == "lui":
            self.execute_lui(state)
        elif self.opcode == "beq":
            return self.execute_beq(state)
        elif self.opcode == "bne":
            return self.execute_bne(state)
        elif self.opcode == "bnez":
            return self.execute_bnez(state)
        elif self.opcode == "blt":
            return self.execute_blt(state)
        elif self.opcode == "mv":
            self.execute_mv(state)
        elif self.opcode == "lw":
            self.execute_lw(state)
        elif self.opcode == "sw":
            self.execute_sw(state)
        elif self.opcode == "call":
            return self.execute_call(state)
        elif self.opcode == "j":
            return self.execute_j(state)
        elif self.opcode == "jalr":
            return self.execute_jalr(state)
        elif self.opcode == "ret":
            return self.execute_ret(state)
        else:
            raise Exception("Execute operand {} not handled.".format(self.opcode))
        return result
