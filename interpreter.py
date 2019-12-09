#!/usr/bin/env python3

import sys
import os
from instruction import *
from parser import RiscvParser
import pickle
from state import RiscvState
from taint import TaintPolicy, TaintTracker
from policy import policy as policy_from_disk
import shutil


MEM_SIZE = 4096
STACK_SIZE = 128
PICKLE_CABINET = "pickle_cabinet"

class RiscvInterpreter():
    """
    Simulates execution of a RISC-V binary.
    """
    def __init__(self, riscv_file, policy):
        self.state = RiscvState(MEM_SIZE, STACK_SIZE)
        self.tracker = TaintTracker(self.state, policy)

        parser = RiscvParser(riscv_file)
        self._instructions = parser.get_instructions()
        self.block_labels = parser.get_labels()

        # Number of pickles created thus far.
        self.pickle_count = 0

        # Current block changes at every jump, call, and return.
        self.current_block = "main"

        # Function changes only during calls and returns.
        self.current_function = "main"

        # Set pc to start at 'main'.
        self.state.set_register('pc', self.block_labels["main"])
        # To help detect when the final return is executed.
        self.state.set_register('ra', -1)

    def get_state(self):
        return self.state

    def get_tracker(self):
        return self.tracker

    def set_corresponding_block(self):
        pc = self.state.get_register('pc')
        prev_val = 0
        # Find the block containing the instruction pointer.
        for key, val in self.block_labels.items():
            if prev_val <= pc and pc <= val:
                block_name = key
            prev_val = val
        self.current_block = block_name
        self.current_function = block_name

    def _run_one(self, instr):
        # Run a single instruction.
        result = instr.execute(self.state, self.tracker)

        if result != 0 and not result:
            raise Exception("unsupported instruction: {}".format(instr.opcode))
            sys.exit(1)
        else:
            # Final return in the program.
            if result == -1:
                return False
            # Return.
            elif result == 0:
                self.set_corresponding_block()
                return True
            # Non-jump instruction.
            elif result == 1:
                pc = self.state.get_register('pc')
                self.state.set_register('pc', pc+1)
                return True
            # Jump or call instruction.
            else:
                self.current_block = result
                if instr.opcode == "call":
                    self.current_function = result
                return True

    def run(self):
        pc = self.state.get_register('pc')
        instr = self._instructions[pc]

        print("\nRUN INSTR {}: {}".format(pc, instr.to_string()))
        return self._run_one(instr)

    def pickle_current_state(self, fileheader, pickle_jar):
        pc = self.state.get_register('pc')
        file = open("{}/pickles/{}-instr{:03d}-line{:03d}".format(pickle_jar,
                    fileheader, self.pickle_count, pc), 'wb')
        self.pickle_count += 1
        pickle.dump(self, file)

    def load_pickled_state(self, pickle_jar, fileheader, pickle_num, pc):
        file = open("{}/pickles/{}-instr{}-line{}".format(pickle_jar, fileheader, pickle_num, pc), 'rb')
        return pickle.load(file)

def main():
    if len(sys.argv) < 2:
        print("Usage: {} <riscv_file> <program_args>"
              .format(sys.argv[0]))
        sys.exit(1)

    riscv_file = sys.argv[1]
    if not os.path.isfile(riscv_file) or riscv_file.split('.')[1] != 's':
        print("'{}' is not a RISC-V assembly file".format(riscv_file))
        sys.exit(1)

    # Create root pickles folder if it doesn't already exist.
    if not os.path.isdir(PICKLE_CABINET):
        os.mkdir(PICKLE_CABINET)

    # Create file specific pickle folder if it doesn't already exist or clears old old pickle folder.
    filename = riscv_file.split('.')[0].replace("/", "_")
    pickle_jar = "{}/jar_{}".format(PICKLE_CABINET, filename)
    if os.path.isdir(pickle_jar):
        shutil.rmtree(pickle_jar)
    os.mkdir(pickle_jar)
    os.mkdir("{}/pickles".format(pickle_jar))
    os.mkdir("{}/data".format(pickle_jar))

    # TODO: handle arguments
    # TODO: implement program_args as single input file
    # program_args = sys.argv[min_args:]


    print("\nBEGINNING EXECUTION...")
    interpreter = RiscvInterpreter(riscv_file, policy_from_disk)

    # Interpreter loop with taint tracking.
    while(interpreter.run()):
        interpreter.pickle_current_state("state", pickle_jar)

    # Return value is stored in 'a0'.
    print("\nRETURN VALUE: ", interpreter.state.get_register('a0'))
    print("\nEXECUTION FINISHED!\n\n####################")
    interpreter.tracker.print_registers_taint()

    return 0


if __name__ == '__main__':
    main()
