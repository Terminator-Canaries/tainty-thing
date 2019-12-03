"""
parsing.py

Defines functions that parse a RISC-V binary.
"""

from instruction import RiscvInstr


# Split out program blocks given a single binary.
def extractBlocks(riscv_file):
    blocks = dict()

    with open(riscv_file, 'r') as file:
        content = file.readlines()
    content = [line.strip("\n") for line in content]

    # Throw away header and footer.
    header_len, footer_len = 7, 13
    content = content[header_len:len(content)-footer_len]

    label_indices = []
    for i in range(len(content)):
        # Seeing ':' indicates delimiter between block labels and blocks.
        if content[i][-1] == ":":
            label_indices.append(i)

    for i in range(len(label_indices)-1):
        idx = label_indices[i]
        block_start = idx + 1
        block_end = label_indices[i+1]
        blocks[content[idx]] = content[block_start:block_end]

    # Last block is a special case.
    last_block_label = label_indices[-1]
    blocks[content[last_block_label]] = content[last_block_label+1:]

    # Remove tab from each instruction.
    for key in blocks.keys():
        cleaned_insns = []
        for instr in blocks[key]:
            if instr[0] == '\t':
               cleaned_insns.append(instr[1:])
            else:
                raise Exception("instruction doesn't begin with a tab")
        blocks[key] = cleaned_insns

    for key in blocks.keys():
        # Log for debugging.
        print("Block: ", key)
        cleanInstructions(blocks, key)


# Parse out instruction opcode and args given single block.
def cleanInstructions(blocks, block_label):
    instructions = blocks[block_label]
    for instr in instructions:
        tokens = instr.replace('\t', ' ').replace(',', '').split(' ')
        # Log for debugging.
        print(tokens)
        instr = RiscvInstr(tokens)
