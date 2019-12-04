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
        self.parsed_content = parsed_content
        self.block_labels_to_lines = block_labels_to_lines

        # Snapshots of state created for each instruction.
        self.pickles = []
        self.pickle_count = 0

        # Need to add instruction policy argument.
        self.taint_policy = TaintPolicy(mem_size, None)

    # Execute instruction if supported, otherwise interpreter fails.
    def run_one(self, state, instr):
        if not instr.execute(state):
            raise Exception("unsupported instruction: {}".format(instr.opcode))
            sys.exit(1)

    # Execute whichever instruction is pointed to by the program counter.
    def run(self, policy):
        # Simulate program counter.
        instr = self.blocks[self.current_block][self.current_line]
        # If taint found, check policies and switch to executing in taint mode.
        if policy.tainted_args(instr):
            policy.propagate(instr)
            # TODO: switch modes
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

    interpreter = RiscvInterpreter(STACK_SIZE, MEM_SIZE, riscv_file, block_labels_to_lines, parsed_content)

    # TODO: add instruction_policy
    policy = TaintPolicy(None)

    # Interpreter loop.
    while(interpreter.run_wrapper(policy)):
        # TODO: logging
        pass

    return interpreter.state.get_arg_value('ra')


if __name__ == '__main__':
    main()
