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


class RiscvState():
    """
    Represents interpreter state on a 32-bit machine.
    """
    def __init__(self, mem_size, stack_size, entry_point=0):
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

    def print(self):
        # Print register contents.
        for register, idx in ABI_TO_REGISTER_IDX.items():
            val = self.registers[idx]
            print("Register ", register, " contains value ", val.get_value(),
                  " with taint ", val.print_taint())
        # Print memory contents.
        for idx, val in enumerate(self.memory):
            print("Memory at location ", idx, " contains value ", val.get_value(),
                  " with taint ", val.print_taint())

    # Update single register or memory location.
    def update(self, arg, update_val):
        if arg.is_register():
            self.state.set_register(arg.register_idx, update_val)
        elif arg.is_memory():
            self.state.set_memory(arg.mem_location, update_val)
        else:
            raise Exception("saw non-register and non-memory instruction argument")

    def print(self):
        # Print register contents.
        for register, idx in ABI_TO_REGISTER_IDX.items():
            val = self.registers[idx]
            print("Register ", register, " contains value ", val.get_value(),
                  " with taint ", val.print_taint())
        # Print memory contents.
        for idx, val in enumerate(self.memory):
            print("Memory at location ", idx, " contains value ", val.get_value(),
                  " with taint ", val.print_taint())

    # Update single register or memory location.
    def update(self, arg, update_val):
        if arg.is_register():
            self.state.set_register(arg.register_idx, update_val)
        elif arg.is_memory():
            self.state.set_memory(arg.mem_location, update_val)
        else:
            raise Exception("saw non-register and non-memory instruction argument")

    def get_arg_val(self, arg):
        if arg.is_register():
            return self.get_register(arg.register_idx)
        elif arg.is_memory():
            return self.get_memory(arg.mem_location)
        else:
            return arg.token

    

    def get_register(self, idx):
        if idx >= 0 and idx <= 32:
            return self.registers[idx]
        else:
            raise Exception("attempt to read invalid register")

    def set_register(self, idx, val):
        if idx >= 0 and idx <= 32:
            self.registers[idx] = val
        else:
            raise Exception("attempt to write to invalid register")

    def get_memory(self, location):
        if location < 0 or location > self.MEM_SIZE:
            raise Exception("memory read out of bounds")
        return self.memory[location]

    def set_memory(self, location, val):
        if location < 0 or location > self.MEM_SIZE:
            raise Exception("memory write out of bounds")
        self.memory[location] = val
