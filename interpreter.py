#!/usr/bin/env python3

import sys
from execution import *
from instruction import *
from parsing import extractBlocks
from state import RiscvState
from taint import ValueTaint, TaintPolicy


MEM_SIZE = 4096
STACK_SIZE = 128


class RiscvInterpreter():
    def __init__(self, mem_size, stack_size, riscv_file, pickle_jar=None):
        self.state = RiscvState(mem_size, stack_size)

        # Parsed representation of RISC-V assembly program blocks.
        self.blocks = extractBlocks(riscv_file)
        # First block in program should be main.
        self.current_block = "main"
        self.current_line = 0

        # Snapshots of state created for each instruction.
        self.pickles = []
        self.pickle_count = 0

        # Need to add instruction policy argument.
        self.taint_policy = TaintPolicy(mem_size, None)

    def print_state(self):
        for key in self.state.keys():
            val = self.state[key]
            print("Register ", key, " contains value ", val.get_value(), " with taint ",
                get_taint_as_string(val.get_taint()))

    # Update single register or memory location.
    def update_state(self, arg, update_val):
        if arg.is_register():
            self.state.set_register(arg.register_idx, update_val)
        elif arg.is_memory():
            self.state.set_memory(arg.mem_location, update_val)
        else:
            raise Exception(
                "saw non-register and non-memory instruction argument"
            )

    # Execute instruction if supported, otherwise interpreter fails.
    def run_one(self, state, instr):
        opcode = instr.opcode
        args = [state.get_arg_val(arg) for arg in instr.args]

        if opcode == "addi":
            update_val = execute_addi(args)
            update_state(instr.args[0])
        elif opcode == "beq":
            if execute_beq(args):
                pass
        elif opcode == "bne":
            if execute_bne(args):
                pass
        elif opcode == "call":
            call_func = args[0]
            # TODO: call function
        elif opcode == "j":
            jump_target = args[0]
            jump_block = blocks[jump_target]
            self.current_block = jump_block
        elif opcode == "lui":
            update_val = execute_lui(args)
            update_state(instr.args[0])
        elif opcode == "lw":
            update_val = execute_lw(args)
            update_state(instr.args[0])
        elif opcode == "sw":
            # TODO: figure out how to reverse 'lw'
            pass
        else:
            raise Exception("unsupported instruction: {}".format(opcode))
            sys.exit(1)

        # Reset line number if jumping to new block.
        if opcode != "j":
            self.current_line += 1
        else:
            self.current_line = 0
        return False

    # Execute the instruction pointed to by the program counter.
    def run_wrapper(self, policy):
        # Simulate program counter.
        instr = self.blocks[self.current_block][self.current_line]
        # If taint found, check policies and switch to executing in taint mode.
        if policy.tainted_args(instr):
            policy.propagate(instr)
            # TODO: switch modes
        return self.run_one(state, instr)


def main():
    min_args = 2
    if len(sys.argv) < min_args:
        # TODO: add in pickling
        print('Usage: {} <riscv_file> <program_args>'
              .format(sys.argv[0]))
        sys.exit(1)

    riscv_file = sys.argv[1]
    
    # TODO: handle arguments
    # program_args = sys.argv[min_args:]

    # TODO: implement as input file

    # TODO: pickling

    interpreter = RiscvInterpreter(STACK_SIZE, MEM_SIZE, riscv_file)
    policy = TaintPolicy()

    # Interpreter loop.
    while(interpreter.run_wrapper(policy)):
        # TODO: logging
        pass

    return state.get_register('ra')


if __name__ == '__main__':
    main()
