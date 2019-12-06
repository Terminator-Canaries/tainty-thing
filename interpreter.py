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
        self.current_block = None

        parser = RiscvParser(riscv_file)
        self._instructions = parser.get_instructions()
        self.block_labels = parser.get_labels()

        # Snapshots of state created for each instruction.
        self.pickles = []
        self.pickle_count = 0

        # Need to add instruction policy argument.
        self.taint_policy = TaintPolicy()

    def _run_one(self, state, instr):
        """
        Run a single instruction.
        """
        result = instr.execute(self.state, self.block_labels)

        # Just executed a jump instruction.
        if result and result != 1:
            self.current_block = result
            return True
        # Just executed a return.
        elif result == 0:
            # Want to return false to stop execution.
            return not (self.current_block == "main:")
        elif not result:
            raise Exception("unsupported instruction: {}".format(instr.opcode))
            sys.exit(1)
        else:
            pc = self.state.get_register(32)
            self.state.set_register(32, pc+1)
            return True

    def run(self):
        pc = self.state.get_register(32)
        instr = self._instructions[pc]
        # logging
        print("\nRUN INSTR: ", instr.to_string())
        print("PROGRAM CTR: ", pc)
        ran = self._run_one(self.state, instr)
        return ran


def main():
    min_args = 2
    if len(sys.argv) < min_args:
        print('Usage: {} <riscv_file> <program_args>'.format(sys.argv[0]))
        sys.exit(1)
    riscv_file = sys.argv[1]

    # TODO: handle arguments
    # TODO: implement program_args as single input file
    # program_args = sys.argv[min_args:]

    # TODO: pickling

    interpreter = RiscvInterpreter(riscv_file)
    interpreter.current_block = "main:"

    policy = TaintPolicy()

    # Interpreter loop with taint tracking.
    while(interpreter.run()):
        policy.num_total_instr_run += 1

    # Return value is stored in 'a0'.
    print("\nRETURN VALUE: ", interpreter.state.get_register(10))
    return 0


if __name__ == '__main__':
    main()
