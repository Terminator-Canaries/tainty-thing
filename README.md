# Tainty Thing

## Setup on OSX

Install llvm

    brew install llvm

## Run the interpreter

#### Generate a RISCV file

    sh gen_riscv.sh file.c


If you get the error "llc: command not found" on OSX,
you can probably fix it by adding `/usr/local/opt/llvm/bin/` to your path:

        echo 'export PATH="/usr/local/opt/llvm/bin:$PATH"' >> ~/.bash_profile

        source ~/.bash_profile

#### Run the interpreter

    python interpreter.py riscv_file program_args

Where `riscv_file` is the generated RISC-V assembly file.

Pickle files will be automatically generated in the folder `pickle_cabinet`.

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
