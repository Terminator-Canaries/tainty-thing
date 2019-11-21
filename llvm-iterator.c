#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <llvm-c/Core.h>
#include <llvm-c/BitReader.h>
#include <llvm-c/BitWriter.h>

void print_instruction_info(LLVMValueRef instruction) {
    if (LLVMIsABinaryOperator(instruction)) {
        printf("\n(binary operator!)\n");
    } else {
        printf("\n");
    }

    printf("instruction: ");

    LLVMOpcode opcode = LLVMGetInstructionOpcode(instruction);
    switch (opcode) {
        case LLVMRet:
            printf("ret\n");
            break;
        case LLVMAdd:
            printf("add\n");
            break;
        case LLVMLoad:
            printf("load\n");
            break;
        case LLVMAlloca:
            printf("alloca\n");
            break;
        case LLVMStore:
            printf("store\n");
            break;
        case LLVMCall:
            printf("call\n");
            break;
        default:
            printf("unrecognized opcode %i\n", opcode);
    }
}

int main(const int argc, const char *const argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: llvm-parser inputfile.bc\n");
        return 1;
    }

    const char *const infile = argv[1];

    // this should be allocated right? docs from LLVMCreateMemoryBuff..
    // aren't great?
    LLVMMemoryBufferRef memoryBuffer;
    char *message;
    int r = LLVMCreateMemoryBufferWithContentsOfFile(infile, &memoryBuffer, &message);
    if (r != 0) {
        fprintf(stderr, "%s\n", message);
        return 1;
    }

    // now create our module using the memorybuffer
    LLVMModuleRef module;

    r = LLVMParseBitcode2(memoryBuffer, &module);
    if (r != 0) {
        fprintf(stderr, "Invalid bitcode detected!\n");
        LLVMDisposeMemoryBuffer(memoryBuffer);
        return 1;
    }

    // done with the memory buffer now, so dispose of it
    LLVMDisposeMemoryBuffer(memoryBuffer);

    // loop through functions
    for (LLVMValueRef fun = LLVMGetFirstFunction(module);
         fun; fun = LLVMGetNextFunction(fun)) {
        printf("loop through function\n");

        // loop through basic blocks
        for (LLVMBasicBlockRef block = LLVMGetFirstBasicBlock(fun);
             block; block = LLVMGetNextBasicBlock(block)) {
                printf("block!\n");

                // loop through instructions
                for (LLVMValueRef instr = LLVMGetFirstInstruction(block);
                     instr; instr = LLVMGetNextInstruction(instr)) {
                        print_instruction_info(instr);
                    }
            }
    }

    LLVMDisposeModule(module);

    return 0;
}
