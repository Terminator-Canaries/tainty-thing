"""
taint.py

Defines object representations necessary to track and propagate taint.
"""

from state import ABI_TO_REGISTER_IDX
from instruction import SUPPORTED_FUNCTIONS, TAINT_LOC, TAINT_UID, TAINT_NAME, TAINT_FACE, TAINT_PASSWORD, TAINT_OTHER

# Defines rules for taint propagation.
class TaintPolicy():
    def __init__(self):
        # Keep track of taint stats.
        self.taint_level = 0
        self.num_total_instr_run = 0
        self.num_tainted_instr_run = 0
        self.time_in_taint_mode = 0


class TaintTracker():
    def __init__(self, state):
        # Physical limits.
        self.STACK_SIZE = state.STACK_SIZE
        self.MEM_SIZE = state.MEM_SIZE
        self.state = state

        # Taint stats.
        self.taint_level = 0
        self.num_total_instr_run = 0
        self.num_tainted_instr_run = 0
        self.time_in_taint_mode = 0

        # Add to taint source when supported function is called.
        # Clear when function returns.
        self.taint_source = 0

        # Shadow state for taint tracking.
        self.shadow_registers = [0 for i in range(33)]
        self.shadow_memory = [0 for i in range(self.MEM_SIZE)]

    def get_reg_idx(self, reg):
        if type(reg).__name__ == 'str' and reg in ABI_TO_REGISTER_IDX:
            return ABI_TO_REGISTER_IDX[reg]
        elif type(reg).__name__ == 'int':
            return reg
        else:
            raise Exception("Invalid reg {}".format(reg))

    # Pretty print the taint mask.
    def print_taint(self, taint):
        if taint == 0:
            return "CLEAN"

        taint_string = ""
        if (taint & TAINT_LOC):
            taint_string += "|TAINT_LOC"
        if (taint & TAINT_UID):
            taint_string += "|TAINT_UID"
        if (taint & TAINT_NAME):
            taint_string += "|TAINT_NAME"
        if (taint & TAINT_FACE):
            taint_string += "|TAINT_FACE"
        if (taint & TAINT_PASSWORD):
            taint_string += "|TAINT_PASSWORD"
        if (taint & TAINT_OTHER):
            taint_string += "|TAINT_OTHER"
        return taint_string[1:]

    # Return the logic OR of two taint masks.
    def combine_taint(self, taint1, taint2):
        return taint1 | taint2

    def get_memory_taint(self, location):
        if location < 0 or location > self.MEM_SIZE:
            raise Exception("Memory read out of bounds")
        return self.shadow_memory[location]

    def replace_memory_taint(self, location, taint):
        if location < 0 or location > self.MEM_SIZE:
            raise Exception("Memory write out of bounds")
        self.shadow_memory[location] = taint

    def add_memory_taint(self, location, taint):
        if location < 0 or location > self.MEM_SIZE:
            raise Exception("Memory write out of bounds")
        self.shadow_memory[location] = self.combine_taint(taint, self.shadow_memory[location])

    def get_register_taint(self, reg):
        idx = self.get_reg_idx(reg)
        if idx >= 0 and idx <= 32:
            return self.shadow_registers[idx]
        else:
            raise Exception("Attempt to read invalid register")

    def replace_register_taint(self, reg, taint):
        idx = self.get_reg_idx(reg)
        if idx >= 0 and idx <= 32:
            self.shadow_registers[idx] = taint
        else:
            raise Exception("Attempt to write to invalid register")

    def add_register_taint(self, reg, taint):
        idx = self.get_reg_idx(reg)
        if idx >= 0 and idx <= 32:
            self.shadow_registers[idx] = self.combine_taint(taint, self.shadow_registers[idx])
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
            mem_location = self.state.get_register(ABI_TO_REGISTER_IDX[base]) + offset
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
            self.replace_register_taint(operand.register_idx, taint)
        elif operand.is_memory():
            base = ABI_TO_REGISTER_IDX[operand.mem_reference.get_base()]
            offset = int(operand.mem_reference.get_offset())
            mem_location = self.state.get_register(base) + offset
            self.add_memory_taint(mem_location, taint)
        else:
            raise Exception("Instruction operand not register or memory")

    # Replaces the operand's taint mask with 'taint'.
    def replace_operand_taint(self, operand, taint):
        if operand.is_register():
            self.replace_register_taint(operand.register_idx, taint)
        elif operand.is_memory():
            base = ABI_TO_REGISTER_IDX[operand.mem_reference.get_base()]
            offset = int(operand.mem_reference.get_offset())
            mem_location = self.state.get_register(base) + offset
            self.replace_memory_taint(mem_location, taint)
        else:
            raise Exception("Instruction operand not register or memory")

    # addi    op0, op1, op2
    # op0 = op1 + sext(op2)
    def taint_addi(self, opcode, operands):
        if len(operands) < 3:
            raise InsufficientOperands()
        taint1 = self.get_operand_taint(operands[1])
        taint2 = self.get_operand_taint(operands[2])
        self.replace_operand_taint(operands[0], self.combine_taint(taint1, taint2))

    # subi    op0, op1, op2
    # op0 = op1 - sext(op2)
    def taint_subi(self, opcode, operands):
        if len(operands) < 3:
            raise InsufficientOperands()
        taint1 = self.get_operand_taint(operands[1])
        taint2 = self.get_operand_taint(operands[2])
        self.replace_operand_taint(operands[0], self.combine_taint(taint1, taint2))

    # beq    op0, op1, op2
    # jump to op2 if op0 == op1
    def taint_beq(self, opcode, operands):
        # TODO - Jump tainting
        return

    # bne    op0, op1, op2
    # jump to op2 if op0 != op1
    def taint_bne(self, opcode, operands):
        # TODO - Jump tainting
        return

    # j    op0
    # jump to op0
    def taint_j(self, opcode, operands):
        # TODO - Jump tainting
        return

    # lui    op0, op1
    # op0 = op1 << 12
    def taint_lui(self, opcode, operands):
        if len(operands) < 2:
            raise InsufficientOperands()
        taint1 = self.get_operand_taint(operands[1])
        self.replace_operand_taint(operands[0], taint1)

    # lw    op0, op1(op2)
    # op0 = val(op2 + op1)
    def taint_lw(self, opcode, operands):
        if len(operands) < 2:
            raise InsufficientOperands()
        taint1 = self.get_operand_taint(operands[1])
        self.replace_operand_taint(operands[0], taint1)

    def taint_ret(self, opcode, operands):
        if len(operands) != 0:
            raise InsufficientOperands()

        # Return address is stored in 'ra'.
        if self.taint_source != 0:
            self.replace_register_taint('a0', self.taint_source)
        self.taint_source = 0
        return

    # sw    op0, op1(op2)
    # val(op2 + op1) <- op0
    def taint_sw(self, opcode, operands):
        if len(operands) < 2:
            raise InsufficientOperands()
        taint1 = self.get_operand_taint(operands[0])
        self.replace_operand_taint(operands[1], taint1)

    # call   op0
    # taint function op0
    def taint_call(self, opcode, operands):
        if len(operands) < 1:
            raise InsufficientOperands()
        elif len(operands) != 1:
            raise Exception("Function args not yet handled.")

        function_name = operands[0].get_target_name()
        if function_name in SUPPORTED_FUNCTIONS:
            self.taint_source = SUPPORTED_FUNCTIONS[function_name]
        else:
            raise Exception("Function {} not taint call supported.".format(function_name))
        return 

    def taint_by_operand(self, state, opcode, operands):
        # Give the object access to the current state.
        self.state = state
        policy[opcode](operands)
        # {'sw': taint_sw}
        # {'addi': function(operands,taintstate,state){ 
        #   if pc == 15 {taintstate[op1] |= taintstate[op2]
        #  }}
        # lines 10 - 15, use instrpolicy a
        # otherwise use b
        # taintpolicy.state.functionlist = ["a","b"]
        # Handle the specified operation.
        if opcode == "addi" or opcode == "add":
            return self.taint_addi(opcode, operands)
        elif opcode == "subi" or opcode == "sub":
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
            raise Exception("Taint opcode '{}' not handled.".format(opcode))

    def print_registers_taint(self):
        print("PRINTING REGISTER TAINT")

        # Shadow state for taint tracking.
        for reg, idx in ABI_TO_REGISTER_IDX.items():
            print("'{}' taint = {}".format(reg, self.print_taint(self.shadow_registers[idx])))
        return

    def print_memory_taint(self):
        # Shadow state for taint tracking.
        for idx in range(len(self.shadow_memory)):
            print("mem {}: taint = {}".format(idx, self.print_taint(self.shadow_memory[idx])))
        return

    def percentage_tainted_registers(self):
        num_tainted = sum([min(1, taint) for taint in self.shadow_registers])
        return num_tainted / len(self.shadow_registers)

    def percentage_tainted_memory(self):
        num_tainted = sum([min(1, taint) for taint in self.shadow_memory])
        return num_tainted / len(self.shadow_memory)






