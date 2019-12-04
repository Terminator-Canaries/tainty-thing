"""
parsing.py

"""

from instruction import RiscvInstr


class RiscvParser():
    """
    Defines a parser for raw RISC-V binary files.
    """
    def __init__(self, bin_file):
        with open(bin_file, 'r') as file:
            self.content = []
            for line in file.readlines():
                line = line.strip("\n")
                if line:
                    self.content.append(line)

    def print_content(self):
        print("RISC-V BINARY:")
        for line in self.content:
            print(line)

    # Split out program blocks given a single binary.
    def extract_blocks(self):
        block_labels_to_lines = dict()
        label_indices = []

        for idx, line in enumerate(self.content):
            # Seeing ':' indicates delimiter between block labels and blocks.
            if line and line[-1] == ":":
                label_indices.append(idx)

        for idx in label_indices:
            block_label = self.content[idx]
            block_labels_to_lines[block_label] = idx

        return block_labels_to_lines

    def parse_lines(self):
        parsed_content = []

        for line in self.content:
            line.strip()
            print("line: ", line)

            # Skip lines until first block reached.
            if line[0] == ".":
                continue

            # Ignore CFI directives and LLVM comments.
            if line[0:3] == ".cfi" or line[0] == "#":
                continue

            # Don't convert block labels to instruction objects.
            if line[-1] != ":":
                line.replace('\t', ' ')
                line.replace(',', '')
                tokens = line.split(' ')
                instr = RiscvInstr(tokens)
                parsed_content.append(instr)
            else:
                parsed_content.append(line)

        return parsed_content
