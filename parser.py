"""
parsing.py

"""

from instruction import RiscvInstr


class RiscvParser():
    """
    Defines a parser for raw RISC-V binary files.
    """
    def __init__(self, bin_file):
        # An array of the lines from the file.
        self._data = []
        # An array of the lines that contain instructions.
        self._instructions = []
        # Mapping of labels to instruction index.
        self._labels = {}

        with open(bin_file, 'r') as file:
            self.data = file.readlines()
            instruction_lines = []
            for line in self.data:
                line = line.strip()

                # Skip blank lines.
                if not line:
                    continue

                # Skip lines like: .file	"program.c" or .cfi_endproc.
                # But not labels like: .Lfunc_end0:
                if line[0] == '.'and ':' not in line:
                    continue

                # Skip lines that are just comments like: # -- End function.
                if line[0] == "#":
                    continue

                # Found a block label.
                if ':' in line:
                    # Strip off the extra comments from labels
                    # Ex.) "main:     # @main" should just be "main:"
                    label = line.split(':')[0]
                    # Map the label to the instruction index.
                    self._labels[label] = len(instruction_lines)
                    continue

                # Found an instruction.
                instruction_lines.append(line)

            for line in instruction_lines:
                self._instructions.append(self._line_to_instruction(line))

    def _line_to_instruction(self, line):
        tokens = [token.strip(',') for token in line.split()]
        return RiscvInstr(tokens, self._labels)

    def print_content(self):
        print("RISC-V BINARY:")
        for line in self._data:
            print(line)

    def get_instructions(self):
        return self._instructions

    def get_labels(self):
        return self._labels
