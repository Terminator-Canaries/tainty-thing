"""
taint.py

Defines object representations necessary to track and propagate taint.

* class TaintTracker - provides taint tracking abstractions for instruction-level tracking.
For each instruction encountered, propagates taint based on the user provided taint policy.
Maintains shadow memory and shadow registers, which correspond to regs/mem in interpreter state.
"""

from collections import defaultdict
from state import ABI_TO_REGISTER_IDX
from instruction import SUPPORTED_FUNCTIONS

from instruction import (
    TAINT_LOC,
    TAINT_UID,
    TAINT_NAME,
    TAINT_FACE,
    TAINT_PASSWORD,
    TAINT_OTHER,
)

# For heavy hitter tracking. Flags to know where taint destination is by opcode.
TAINT_DEST = {
    "addi": 0,
    "add": 0,
    "sub": 0,
    "subi": 0,
    "and": 0,
    "andi": 0,
    "xor": 0,
    "xori": 0,
    "srl": 0,
    "srli": 0,
    "sll": 0,
    "slli": 0,
    "sw": 1,
    "call": "call",
    "mv": 0,
    "ret": "ret",
    "lw": 0,
    "blt": "jump",
    "bne": "jump",
    "bnez": "jump",
    "beq": "jump",
    "j": "jump",
    "jalr": "jump",
    "lui": 0
}

class TaintTracker:
    def __init__(self, state, policy):
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

        self.policy = policy

        # Shadow state for taint tracking.
        self.shadow_registers = [0 for i in range(33)]
        self.shadow_memory = [0 for i in range(self.MEM_SIZE)]

        # For Heavy Hitter tracking.
        # For each instruction line, stores whether taint was propogated.
        self.propagation_history = defaultdict(list)

    def get_reg_idx(self, reg):
        if type(reg).__name__ == "str" and reg in ABI_TO_REGISTER_IDX:
            return ABI_TO_REGISTER_IDX[reg]
        elif type(reg).__name__ == "int":
            return reg
        else:
            raise Exception("Invalid reg {}".format(reg))

    # Pretty print the taint mask.
    def print_taint(self, taint):
        if taint == 0:
            return "CLEAN"

        taint_string = ""
        if taint & TAINT_LOC:
            taint_string += "|TAINT_LOC"
        if taint & TAINT_UID:
            taint_string += "|TAINT_UID"
        if taint & TAINT_NAME:
            taint_string += "|TAINT_NAME"
        if taint & TAINT_FACE:
            taint_string += "|TAINT_FACE"
        if taint & TAINT_PASSWORD:
            taint_string += "|TAINT_PASSWORD"
        if taint & TAINT_OTHER:
            taint_string += "|TAINT_OTHER"
        return taint_string[1:]

    # Return the logic OR of two taint masks.
    def OR(self, taint1, taint2):
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
        self.shadow_memory[location] = self.OR(
            taint, self.shadow_memory[location]
        )

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
            self.shadow_registers[idx] = self.OR(
                taint, self.shadow_registers[idx]
            )
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
            raise Exception(
                "Operand is a label. Use operand.get_target_name() instead."
            )
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

    def taint_by_operand(self, state, opcode, operands):
        if opcode not in self.policy:
            raise Exception("Taint opcode '{}' not handled.".format(opcode))
        self.policy[opcode](tracker=self, state=state, operands=operands)

        # For Heavy Hitter data
        self.propagation_history_track(opcode, operands)

    # Determines whether taint was propagated.
    # Updates internal propagation_history dictionary.
    def propagation_history_track(self, opcode, operands):
        strategy = TAINT_DEST[opcode]
        is_tainted_line = 0

        if strategy == 0 or strategy == 1:
            is_tainted_line = self.get_operand_taint(operands[strategy])
        elif strategy == "call":
            if operands[0].to_string() in SUPPORTED_FUNCTIONS:
                is_tainted_line = SUPPORTED_FUNCTIONS[operands[0].to_string()]
        elif not strategy == "ret" and not strategy == "jump":
            raise Exception("Strategy {} not handled.".format(strategy))

        pc = self.state.get_register('pc')
        self.propagation_history[pc].append(is_tainted_line)

    def print_registers_taint(self):
        print("\nREGISTER TAINT:")

        # Shadow state for taint tracking.
        for reg, idx in ABI_TO_REGISTER_IDX.items():
            print(
                "'{}' taint = {}".format(
                    reg, self.print_taint(self.shadow_registers[idx])
                )
            )
        return

    def print_only_tainted_registers(self):
        print("REGISTER TAINT:")

        # Shadow state for taint tracking.
        for reg, idx in ABI_TO_REGISTER_IDX.items():
            if self.shadow_registers[idx]:
                print(
                    "'{}' taint = {}".format(
                        reg, self.print_taint(self.shadow_registers[idx])
                    )
                )
        return

    def print_memory_taint(self):
        # Shadow state for taint tracking.
        for idx in range(len(self.shadow_memory)):
            print(
                "mem {}: taint = {}".format(
                    idx, self.print_taint(self.shadow_memory[idx])
                )
            )
        return

    def percentage_tainted_registers(self):
        num_tainted = sum([min(1, taint) for taint in self.shadow_registers])
        return num_tainted / len(self.shadow_registers)

    def percentage_tainted_memory(self):
        num_tainted = sum([min(1, taint) for taint in self.shadow_memory])
        return num_tainted / len(self.shadow_memory)
