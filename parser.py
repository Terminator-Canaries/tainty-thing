"""
parsing.py

"""

from instruction import RiscvInstr


class RiscvParser():
    """
    Defines a parser for raw RISC-V binary files.
    """
    def __init__(self, bin_file):
        # an array of the lines from the file
        self._data = []
        # an array of the lines that contain instructions
        self._instructions = []
        # mapping of labels to instruction index
        self._labels = {}

        with open(bin_file, 'r') as file:
            self.data = file.readlines()
            for line in self.data:
                line = line.strip().strip("\n").strip("\t")

                # skip blank lines
                if not line:
                    continue

                # skip lines like: .file	"program.c" or .cfi_endproc
                # but not lables like: .Lfunc_end0:
                if line[0] == '.'and ':' not in line:
                    continue

                # skip lines that are just comments like: # -- End function
                if line[0] == "#":
                    continue

                # found a label
                if ':' in line:
                    # strip off the extra comments from labels
                    # for example "main:     # @main" should just be "main:"
                    label = line.split()[0]
                    # map the label to the instruction index
                    self._labels[label] = len(self._instructions)
                    continue

                # found an instruction
                self._instructions.append(self._line_to_instruction(line))

    def _line_to_instruction(self, line):
        tokens = line.split()
        for token in tokens:
            token = token.replace(',', '')
        return RiscvInstr(tokens)

    def print_content(self):
        print("RISC-V BINARY:")
        for line in self._data:
            print(line)

    def instructions(self):
        return self._instructions

    def labels(self):
        return self._labels
