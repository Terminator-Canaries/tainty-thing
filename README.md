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

Parses RISC binary.

#### Interpreting

`interpreter.py`

Interprets parsed RISC.

`state.py`

Holds registers and memory. Converts instructions in blocks dictionary into instruction objects.

`execution.py`

Defines functions that execute most common RISC instructions.

`instruction.py`

Defines an object representation for RISC-V instructions.

#### Tainting

`taint.py`

Defines object representations necessary to track and propagate taint.

`backtrack.py`

A proof of concept that our snapshotting works, and that snapshots contain enough
critical information to execute like normal from a saved snapshot.

#### Analysis

`analyze.py`
