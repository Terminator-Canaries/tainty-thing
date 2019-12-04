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
            content = file.readlines()
        content = [line.strip("\n") for line in content]

        # Throw away header and footer.
        header_len, footer_len = 7, 13
        self.content = content[header_len:len(content)-footer_len]

    def print_content(self):
        print("RISC-V BINARY:")
        for line in self.content:
            print(line)

    # Split out program blocks given a single binary.
    def extract_blocks(self):
        block_labels_to_lines = dict()
        label_indices = []

        for line, idx in enumerate(self.content):
            # Seeing ':' indicates delimiter between block labels and blocks.
            if line[-1] == ":":
                label_indices.append(idx)

        for idx in label_indices:
            block_label = self.content[idx]
            self.block_labels_to_lines[block_label] = idx

        return block_labels_to_lines

    def parse_lines(self):
        parsed_content = []

        for line in self.content:
            line.strip('\n').strip('\t')
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
