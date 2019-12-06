#!/usr/bin/env python3

import sys
from execution import *
from instruction import *
from parser import RiscvParser
from state import RiscvState
from taint import ValueTaint, TaintPolicy

MEM_SIZE = 4096
STACK_SIZE = 128

class RiscvInterpreter():
    """
    Simulates execution of a RISC-V binary.
    """
    def __init__(self, riscv_file):
        self.state = RiscvState(MEM_SIZE, STACK_SIZE)

        parser = RiscvParser(riscv_file)
        self._instructions = parser.get_instructions()
        self.block_labels = parser.get_labels()

        # Snapshots of state created for each instruction.
        self.pickles = []
        self.pickle_count = 0

        # Need to add instruction policy argument.
        self.taint_policy = TaintPolicy()

        # Current block changes at every jump, call, and return.
        self.current_block = "main"
        
        # Function changes only during calls and returns.
        self.current_function = "main"  

        # Set pc to start at 'main'.
        self.state.set_register('pc', self.block_labels["main"])

    # Get the block containing the instruction pointer.
    def set_corresponding_block(self):
        pc = self.state.get_register('pc')
        block_name, block_val = None, 0
        for key, val in self.block_labels.items():
            if block_val <= pc and val <= pc:
                block_name = key
                block_val = val

        self.current_block = block_name
        self.current_function = block_name
        return


    def _run_one(self, state, instr):
        """
        Run a single instruction.
        """
        result = instr.execute(self.state)

        # Just executed a jump or call instruction.
        if result and result != 1:
            self.current_block = result
            if instr.opcode == "call":
                self.current_function = result
            return True
        # Just executed a return.
        elif result == 0:
            if self.current_function == "main":
                # Returning from main, so terminate the program. 
                return False  

            # Else, update the current_function and block data.
            self.set_corresponding_block()
            return True
        elif not result:
            raise Exception("unsupported instruction: {}".format(instr.opcode))
            sys.exit(1)

        else:
            pc = self.state.get_register('pc')
            self.state.set_register('pc', pc+1)
            return True

    def run(self):
        pc = self.state.get_register('pc')
        instr = self._instructions[pc]
        
        # logging
        print("\nRUN INSTR {}: {}".format(pc, instr.to_string()))

        return self._run_one(self.state, instr)


def main():
    min_args = 3
    if len(sys.argv) < min_args:
        print('Usage: {} <riscv_file> <pickle_jar> <program_args>'.format(sys.argv[0]))
        sys.exit(1)
    print("sys.argv[1]: {}".format(sys.argv))
    riscv_file = sys.argv[1]
    pickle_jar = sys.argv[2]

    # TODO: handle arguments
    # TODO: implement program_args as single input file
    # program_args = sys.argv[min_args:]

    interpreter = RiscvInterpreter(riscv_file)

    policy = TaintPolicy()

    # Interpreter loop with taint tracking.
    while(interpreter.run()):
        policy.num_total_instr_run += 1
        interpreter.state.pickle_current_state("state", pickle_jar)

    # Return value is stored in 'a0'.
    print("\nRETURN VALUE: ", interpreter.state.get_register('a0'))
    return 0


if __name__ == '__main__':
    main()
