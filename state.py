"""
state.py

"""

ABI_TO_REGISTER_IDX = {
        'zero': 0,
        'ra': 1,
        'sp': 2,
        'gp': 3,
        'tp': 4,
        't0': 5,
        't1': 6,
        't2': 7,
        's0': 8,
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


class RiscvState():
    """
    Represents interpreter state on a 32-bit machine.
    """
    def __init__(self, mem_size, stack_size):
        # Need 32 registers + the program counter.
        self.registers = [0 for i in range(33)]
        # To keep track of taint for each register.
        self.shadow_registers = [0 for i in range(33)]

        self.STACK_SIZE = stack_size
        self.MEM_SIZE = mem_size

        self.memory = [0 for i in range(mem_size)]
        # To keep track of taint for each byte in memory.
        self.shadow_memory = [0 for i in range(mem_size)]

        # Initialize the stack pointer to the end of memory.
        self.set_register(2, mem_size)
        # Set the program counter to the first instruction.
        self.set_register(32, 0)

    def print_registers(self):
        for register, idx in ABI_TO_REGISTER_IDX.items():
            val = self.registers[idx]
            print("Register {} contains value {}".format(register, val))
        
    def print_memory(self):
        for idx, val in enumerate(self.memory):
            print("Memory at location {} contains value {}".format(idx, val))

    def update_val(self, operand, update_val):
        if operand.is_register():
            self.set_register(operand.register_idx, update_val)
        elif operand.is_memory():
            base = ABI_TO_REGISTER_IDX[operand.mem_reference.get_base()]
            offset = int(operand.mem_reference.get_offset())
            mem_location = self.get_register(base) + offset
            self.set_memory(mem_location, update_val)
        else:
            raise Exception("Instruction operand not registor or memory")

    def get_operand_val(self, operand):
        """
        Returns the integer value of the given operand.
        """
        if operand.is_register():
            return self.get_register(operand.register_idx)
        elif operand.is_memory():
            base = operand.mem_reference.get_base()
            offset = int(operand.mem_reference.get_offset())
            if operand.is_valid_register(base) is not None:
                mem_location = self.get_register(ABI_TO_REGISTER_IDX[base]) + offset
                return self.get_memory(mem_location)
            else:
                raise Exception("Base is not a valid register")
        elif operand.is_constant():
            return operand.constant
        else:
            print("Operand is not register, memory reference, or constant")
            return operand.token

    def get_register(self, idx):
        if idx >= 0 and idx <= 32:
            return self.registers[idx]
        else:
            raise Exception("Attempt to read invalid register")

    def set_register(self, idx, val):
        if idx >= 0 and idx <= 32:
            self.registers[idx] = val
        else:
            raise Exception("Attempt to write to invalid register")

    def get_memory(self, location):
        if location < 0 or location > self.MEM_SIZE:
            raise Exception("Memory read out of bounds")
        return self.memory[location]

    def set_memory(self, location, val):
        if location < 0 or location > self.MEM_SIZE:
            raise Exception("Memory write out of bounds")
        self.memory[location] = val
