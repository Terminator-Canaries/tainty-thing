"""
state.py

Defines an object representation for interpreter state.
Includes registers for 32-bit RISC-V, raw memory, and stack memory.
"""

from instruction import *


ABI_TO_REGISTER_IDX = {
        'Zero': 0,
        'zero': 0,
        'ra': 1,
        'sp': 2,
        'gp': 3,
        'tp': 4,
        't0': 5,
        't1': 6,
        't2': 7,
        's0': 8,
        'fp': 8,
        's1': 9,
        'a0': 10,
        'a1': 11,
        'a2': 12,
        'a3': 13,
        'a4': 14,
        'a5': 15,
        'a6': 16,
        'a7': 17,
        's2': 18,
        's3': 19,
        's4': 20,
        's5': 21,
        's6': 22,
        's7': 23,
        's8': 24,
        's9': 25,
        's10': 26,
        's11': 27,
        't3': 28,
        't4': 29,
        't5': 30,
        't6': 31,
        'pc': 32
}

def isValidRegister(name):
    if token in ABI_TO_REGISTER_IDX:
        return ABI_TO_REGISTER_IDX[token]
    else:
        return None

class RiscvState():
    def __init__(self, mem_size, stack_size, entry_point):
        # Need 32 registers + the program counter.
        self.registers = [0 for i in range(33)]
        # To keep track of taint for each register.
        self.shadow_registers = [0 for i in range(33)]

        self.STACK_SIZE = stack_size
        self.MEM_SIZE = mem_size

        self.memory  = [0 for i in range(mem_size)]
        # To keep track of taint for each byte in memory.
        self.shadow_memory = [0 for i in range(mem_size)]

        # Initialize the stack pointer to the end of memory.
        self.setRegister(2, mem_size)
        # Set the program counter to the first instruction.
        self.setRegister(32, entry_point)

    def getArgVal(arg):
        if arg.type == ARG_REGISTER:
            return getRegister(arg.register_idx)
        elif arg.type == ARG_MEMORY:
            return getMemory(arg.mem_location)
        else:
            return arg.token

    def getRegister(idx):
        if idx >= 0 and idx <= 32:
            return self.registers[register_idx]
        else:
            raise Exception("attempt to read invalid register")
            return None

    def setRegister(idx, val):
        if idx >= 0 and idx <= 32:
            self.registers[idx] = val
        else:
            raise Exception("attempt to write to invalid register")

    def getMemory(location):
        if location < 0 or location > self.MEM_SIZE:
            raise Exception("memory read out of bounds")
            return None
        return self.memory[location]

    def setMemory(location, val):
        if location < 0 or location > self.MEM_SIZE:
            raise Exception("memory write out of bounds")
        self.memory[location] = val
