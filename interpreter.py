#!/usr/bin/env python3

import sys
import os
from execution import *
from instruction import *
from parser import RiscvParser
from state import RiscvState
from taint import ValueTaint, TaintPolicy, TaintTracker
import shutil

MEM_SIZE = 4096
STACK_SIZE = 128
PICKLE_CABINET = "pickle_cabinet"

class RiscvInterpreter():
    """
    Simulates execution of a RISC-V binary.
    """
    def __init__(self, riscv_file):
        self.state = RiscvState(MEM_SIZE, STACK_SIZE)
        self.tracker = TaintTracker(self.state)

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


    def _run_one(self, instr):
        """
        Run a single instruction.
        """
        result = instr.execute(self.state, self.tracker)

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

        ran = self._run_one(instr)
        self.tracker.print_registers_taint()
        return ran


def main():
    if len(sys.argv) < 2:
        print("Usage: {} <riscv_file> <program_args>"
              .format(sys.argv[0]))
        sys.exit(1)
    print("sys.argv[1]: {}".format(sys.argv))

    riscv_file = sys.argv[1]
    if not os.path.isfile(riscv_file) or riscv_file.split('.')[1] != 's':
        print("'{}' is not a RISC-V assembly file".format(riscv_file))
        sys.exit(1)

    # Create root pickles folder if it doesn't already exist
    if not os.path.isdir(PICKLE_CABINET):
        os.mkdir(PICKLE_CABINET)

    # Create file specific pickle folder if it doesn't already exist
    # Or clear old old pickle folder
    filename = riscv_file.split('.')[0].replace("/", "_")
    pickle_jar = "{}/jar_{}".format(PICKLE_CABINET, filename)
    if os.path.isdir(pickle_jar):
        shutil.rmtree(pickle_jar)
    os.mkdir(pickle_jar)

    if not os.path.isdir(pickle_jar):
        print("Pickle folder provided '{}' is not a valid directory"
              .format(pickle_jar))
        sys.exit(1)

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
    interpreter.tracker.print_registers_taint()

    return 0


if __name__ == '__main__':
    main()
