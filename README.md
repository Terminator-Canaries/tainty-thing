# Tainty Thing

## Setup on OSX

#### Install llvm:

    brew install llvm

#### Install Python 3.6 or higher

#### Optionally isolate your python environment with a tool like `virtualenv`:

* Install: `pip install virtualenv`

* Create: `virtualenv venv`

* Activate: `source venv/bin/activate`

* Deactivate: `deactivate`

#### Install python dependencies:

    pip install -r requirements.txt

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

Parses RISC binary. Tokenizes instruction-bearing lines.
Stores file lines in '_data'.
Stores tokenized instructions in '_instructions'.

#### Interpreting

`interpreter.py`

Interpreter parses a RISCV file. 

Executes the binary, tracking taint according to the dynamic policy (default policy is in policy.py)
* main - handles arguments, sets up pickling, initializes interpreter, sets up policy
* class RiscvInterpreter - Runs the program instruction by instruction, taking snapshots regularly.

`state.py`

Holds registers and memory. Converts instructions in blocks dictionary into instruction objects.

* ABI_TO_REGISTER_IDX - Maps RISCV instruction names to enumerations.
* class RiscvState - State metadata, an array for memory, and a dictionary for register state.

`instruction.py`

Defines an object representation for RISC-V instructions.

* class RiscvInstr - Parses tokens and creates an object for executing instructions.
* class RiscvOperand - Represents an abstract righthand side operand.
Stores information relevant to classifying operand types (mem refs, consts, regs).
* class MemoryReference - Abstraction for representing mem reference operands. 

#### Tainting

`taint.py`

Defines object representations necessary to track and propagate taint.

* class TaintTracker - provides taint tracking abstractions for instruction-level tracking.
For each instruction encountered, propagates taint based on the user provided taint policy.
Maintains shadow memory and shadow registers, which correspond to regs/mem in interpreter state.

`backtrack.py`

A proof of concept showing our taint tracking interpreter is capable of uploading snapshots 
and executing them easily. This feature is essential for a dynamic taint tracking system, 
allowing the potential for increasing/decreasing taint policies mid-program execution.

# Example Execution.
#python backtrack.py --pickle_path=<path to a pickled state>

`policy.py`
Defines the developer's taint propagation policy. A policy is a mapping of RISC-V instruction
names as strings to a handler.

A handler is a function of 3 arguments, the taint tracker (defined in taint.py), the state of
the interpreter (defined in state.py), and the operands object (defined in instruction.py)

`analyze.py`

Provides abstractions for plotting the change in register/memory taint across the 
execution of the program. 
Outputs generated graphs to the directory <pickle_jar_path>/data/
--memory_graph and --register_graph flags determine which graphs to generate.

* class Analyzer - Uploads the snapshotted state from the specified pickle_jar.

# Example Execution.
# analyzer.py --pickle_jar=<pickle_jar_path> --memory_graph --register_graph
