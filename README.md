# Tainty Thing

## Setup on OSX

Install llvm

    brew install llvm

Add `/usr/local/opt/llvm/bin/` to your path

    echo 'export PATH="/usr/local/opt/llvm/bin:$PATH"' >> ~/.bash_profile

    source ~/.bash_profile

## Run the interpreter

#### Generate a RISCV file

Generate LLVM bytecode `.bc`:   

    clang -c -emit-llvm program.c -o program.bc

Generate a `.s` file:  

    llc -regalloc=basic -march=riscv32 program.bc

#### Run the interpreter

    python interpreter.py riscv_file pickle_jar program_args

## Files

#### Parsing

`parser.py`

Parses RISC binary.

#### Interpreting

`interpreter.py`

Interprets parsed RISC.

* class RiscvInterpreter
* main - handles arguments, sets up pickling, initializes interpreter, sets up policy

`state.py`

Holds registers and memory. Converts instructions in blocks dictionary into instruction objects.

* ABI_TO_REGISTER_IDX
* is_valid_register
* class RiscvState
	
`execution.py`

Defines functions that execute most common RISC instructions.

`instruction.py`

Defines an object representation for RISC-V instructions.

* class RiscvArg
* class RiscvInstr

#### Tainting

`taint.py`

Defines object representations necessary to track and propagate taint.
