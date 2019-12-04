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
    def __init__(self, mem_size, stack_size, parsed_content, block_labels_to_lines):
        self.state = RiscvState(mem_size, stack_size)
        self.current_block = None

        self.parsed_content = parsed_content
        self.block_labels_to_lines = block_labels_to_lines

        # Snapshots of state created for each instruction.
        self.pickles = []
        self.pickle_count = 0

        # Need to add instruction policy argument.
        self.taint_policy = TaintPolicy()

    def run_one(self, state, instr):
        result = instr.execute(self.state, self.block_labels_to_lines)
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
            return True

    def run(self):
        pc = self.state.get_register(32)
        instr = self.parsed_content[pc]
        return self.run_one(self.state, instr)


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

    parser = RiscvParser(riscv_file)
    block_labels_to_lines = parser.extract_blocks()
    parsed_content = parser.parse_lines()

    interpreter = RiscvInterpreter(STACK_SIZE, MEM_SIZE, parsed_content, block_labels_to_lines)

    # TODO: add instruction_policy
    policy = TaintPolicy()

    # Interpreter loop with taint tracking.
    while(interpreter.run()):
        policy.num_total_instr_run += 1

    # Return value stored in 'ra'.
    return interpreter.state.get_register(1)


if __name__ == '__main__':
    main()
