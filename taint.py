"""
instruction.py

Defines object representations necessary to track and propagate taint.
"""

# Taint Flags
# If flags change, edit function get_taint_as_string().
TAINT_LOC = 0x1
TAINT_ID = 0x10
TAINT_NAME = 0x100
TAINT_FACE = 0x1000
TAINT_PASSWORD = 0x10000
TAINT_OTHER = 0x100000


class ValueTaint():
    """
    Represents the combination of a value and its taint.
    """
    def __init__(self, value, taint):
        self.value = value
        self.taint = taint

    def get_value(self):
        return self.value

    def get_taint(self):
        return self.taint

    def add_taint(self, taint):
        self.taint |= taint

    def remove_taint(self, taint):
        self.taint ^= taint

    def print_taint(self, taint):
        taint_string = ""
        if (taint & TAINT_LOC):
            taint_string += "|TAINT_LOC"
        if (taint & TAINT_ID):
            taint_string += "|TAINT_ID"
        if (taint & TAINT_NAME):
            taint_string += "|TAINT_NAME"
        if (taint & TAINT_FACE):
            taint_string += "|TAINT_FACE"
        if (taint & TAINT_PASSWORD):
            taint_string += "|TAINT_PASSWORD"
        if (taint & TAINT_OTHER):
            taint_string += "|TAINT_OTHER"
        return taint_string[1:]


# Defines rules for taint propagation.
class TaintPolicy():
    def __init__(self):
        # Keep track of taint stats.
        self.taint_level = 0
        self.num_total_instr_run = 0
        self.num_tainted_instr_run = 0
        self.time_in_taint_mode = 0

    # True iff tokens are tainted.
    def tainted_args(self, instr):
        # TODO: implement taint checking
        pass

    def propagate_taint(self, instr):
        self.num_tainted_instructions_run += 1
        # TODO: implement taint propagation



class TaintTracker():
    def __init__(self, state):
        # Physical limits.
        self.STACK_SIZE = state.STACK_SIZE
        self.MEM_SIZE = state.MEM_SIZE

        # Taint stats.
        self.taint_level = 0
        self.num_total_instr_run = 0
        self.num_tainted_instr_run = 0
        self.time_in_taint_mode = 0

        # Shadow state for taint tracking.
        self.shadow_registers = [0 for i in range(33)]
        self.shadow_memory = [0 for i in range(mem_size)]

    def get_reg_idx(self, reg):
        if type(reg).__name__ == 'str' and reg in ABI_TO_REGISTER_IDX:
            return ABI_TO_REGISTER_IDX[reg]
        elif type(reg).__name__ == 'int':
            return reg
        else:
            raise Exception("Invalid reg {}".format(reg))

    def get_memory_taint(self, location):
        if location < 0 or location > self.MEM_SIZE:
            raise Exception("Memory read out of bounds")
        return self.shadow_memory[location]

    def set_memory_taint(self, location, taint):
        if location < 0 or location > self.MEM_SIZE:
            raise Exception("Memory write out of bounds")
        self.shadow_memory[location] = taint

    def add_memory_taint(self, location, taint):
        if location < 0 or location > self.MEM_SIZE:
            raise Exception("Memory write out of bounds")
        self.shadow_memory[location] = taint | self.shadow_memory[location]


    def get_register_taint(self, reg):
        idx = self.get_reg_idx(reg)
        if idx >= 0 and idx <= 32:
            return self.registers[idx]
        else:
            raise Exception("Attempt to read invalid register")

    def set_register_taint(self, reg, taint):
        idx = self.get_reg_idx(reg)
        if idx >= 0 and idx <= 32:
            self.registers[idx] = taint
        else:
            raise Exception("Attempt to write to invalid register")

    def add_register_taint(self, reg, taint):
        idx = self.get_reg_idx(reg)
        if idx >= 0 and idx <= 32:
            self.registers[idx] = taint | self.registers[idx]
        else:
            raise Exception("Attempt to write to invalid register")

    def get_operand_taint(self, operand):
        """
        Returns the integer value of the given operand.
        """
        if operand.is_register():
            return self.get_register_taint(operand.register_idx)
        elif operand.is_memory():
            base = operand.mem_reference.get_base()
            offset = int(operand.mem_reference.get_offset())
            mem_location = state.get_register(ABI_TO_REGISTER_IDX[base]) + offset
            return self.get_memory_taint(mem_location)
        elif operand.is_constant():
            return 0  # Constants have no inherent taint.
        elif operand.is_label():
            raise Exception("Operand is a label. Use operand.get_target_name() instead.")
        else:
            raise Exception("Operand is not register, memory reference, or constant")

    # Add taint to the operand's taint mask. 
    def add_operand_taint(self, operand, taint):
        if operand.is_register():
            self.set_register_taint(operand.register_idx, taint)
        elif operand.is_memory():
            base = ABI_TO_REGISTER_IDX[operand.mem_reference.get_base()]
            offset = int(operand.mem_reference.get_offset())
            mem_location = state.get_register(base) + offset
            self.set_memory_taint(mem_location, taint)
        else:
            raise Exception("Instruction operand not register or memory")

    # Replaces the operand's taint mask with 'taint'.
    def replace_operand_taint(self, operand, taint):
        if operand.is_register():
            self.set_register(operand.register_idx, update_val)
        elif operand.is_memory():
            base = ABI_TO_REGISTER_IDX[operand.mem_reference.get_base()]
            offset = int(operand.mem_reference.get_offset())
            mem_location = state.get_register(base) + offset

            self.set_memory(mem_location, update_val)
        else:
            raise Exception("Instruction operand not register or memory")

    # Return the logic OR of two taint masks.
    def combine_taint(self, taint1, taint2):
        return taint1 | taint2

    # addi    op0, op1, op2
    # op0 = op1 + sext(op2)
    def taint_addi(self, opcode, operands):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        # Technically op2 is sign extended but doesn't matter in Python.
        taint1 = self.get_operand_taint(self.operands[1])
        taint2 = self.get_operand_taint(self.operands[2])
        self.update_taint(self.operands[0], self.combine_taint(taint1, taint2))

    # subi    op0, op1, op2
    # op0 = op1 - sext(op2)
    def taint_subi(self, opcode, operands):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        # Technically op2 is sign extended but doesn't matter in Python.
        val1 = state.get_operand_val(self.operands[1])
        val2 = state.get_operand_val(self.operands[2])
        update_val = val1 - val2
        state.update_val(self.operands[0], update_val)

    # beq    op0, op1, op2
    # jump to op2 if op0 == op1
    def taint_beq(self, opcode, operands):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        branch_val = (self.operands[2]).get_target_name()
        pc = self.get_jump_target(branch_val)
        if state.get_operand_val(self.operands[0]) == state.get_operand_val(self.operands[1]):
            state.set_register('pc', pc)
            return branch_val
        else:
            return 1  # no_jump

    # bne    op0, op1, op2
    # jump to op2 if op0 != op1
    def taint_bne(self, opcode, operands):
        if len(self.operands) < 3:
            raise InsufficientOperands()
        branch_val = (self.operands[2]).get_target_name()
        pc = self.get_jump_target(branch_val)
        if state.get_operand_val(self.operands[0]) != state.get_operand_val(self.operands[1]):
            state.set_register('pc', pc)
            return branch_val
        else:
            return 1  # no_jump

    # j    op0
    # jump to op0
    def taint_j(self, opcode, operands):
        if len(self.operands) < 1:
            raise InsufficientOperands()
        jump_val = (self.operands[0]).get_target_name()
        pc = self.get_jump_target(jump_val)
        state.set_register('pc', pc)
        return jump_val

    # lui    op0, op1
    # op0 = op1 << 12
    def taint_lui(self, opcode, operands):
        if len(self.operands) < 2:
            raise InsufficientOperands()
        update_val = state.get_operand_val(self.operands[1]) << 12
        state.update_val(self.operands[0], update_val)

    # lw    op0, op1(op2)
    # op0 = val(op2 + op1)
    def taint_lw(self, opcode, operands):
        if len(self.operands) < 2:
            raise InsufficientOperands()
        mem_reference = self.generate_mem_operand(self.operands[1], state)
        load_val = state.get_operand_val(mem_reference)
        state.update_val(self.operands[0], load_val)

    def taint_ret(self, opcode, operands):
        if len(self.operands) != 0:
            raise InsufficientOperands()
        # Return address is stored in 'ra'.
        ra = state.get_register('ra')
        state.set_register('pc', ra)

    # sw    op0, op1(op2)
    # val(op2 + op1) = op0
    def taint_sw(self, opcode, operands):
        if len(self.operands) < 2:
            raise InsufficientOperands()
        mem_reference = self.generate_mem_operand(self.operands[1], state)
        store_val = state.get_operand_val(self.operands[0])
        state.update_val(mem_reference, store_val)

    # call   op0
    # taint function op0
    def taint_call(self, opcode, operands):
        if len(self.operands) < 1:
            raise InsufficientOperands()
        elif len(self.operands) != 1:
            raise Exception("Function args not yet handled.")
        
        # Set the return address in 'ra' to 'pc'+1.
        pc = state.get_register('pc')
        state.set_register('ra', pc+1)

        # Jump to the function name.
        jump_val = (self.operands[0]).get_target_name()
        pc = self.get_jump_target(jump_val)
        state.set_register('pc', pc)

        return jump_val 

    def taint_by_operand(self, opcode, operands):
        if opcode == "addi" or opcode == "add":
            return self.taint_addi(opcode, operands)
        elif opcode == "subi" or self.opcode == "sub":
            return self.taint_subi(opcode, operands)
        elif opcode == "beq":
            return self.taint_beq(opcode, operands)
        elif opcode == "bne":
            return self.taint_bne(opcode, operands)
        elif opcode == "call":
            return self.taint_call(opcode, operands)
        elif opcode == "j":
            return self.taint_j(opcode, operands)
        elif opcode == "lui":
            return self.taint_lui(opcode, operands)
        elif opcode == "lw":
            return self.taint_lw(opcode, operands)
        elif opcode == "ret":
            return self.taint_ret(opcode, operands)
        elif opcode == "sw":
            return self.taint_sw(opcode, operands)
        else:
            raise Exception("Taint operand not handled.")









