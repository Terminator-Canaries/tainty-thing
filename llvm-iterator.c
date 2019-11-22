#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <llvm-c/Core.h>
#include <llvm-c/BitReader.h>
#include <llvm-c/BitWriter.h>

void print_instruction_info(LLVMValueRef instruction) {
    printf("\n");

    // Get the opcode for this instruction
    // There are many more, only handling a few cases here for example
    LLVMOpcode opcode = LLVMGetInstructionOpcode(instruction);
    switch (opcode) {
        case LLVMRet:
            printf("__ret__\n");
            break;
        case LLVMAdd:
            printf("__add__\n");
            break;
        case LLVMLoad:
            printf("__load__\n");
            break;
        case LLVMAlloca:
            printf("__alloca__\n");
            break;
        case LLVMStore:
            printf("__store__\n");
            break;
        case LLVMCall:
            printf("__call__\n");
            break;
        default:
            printf("unrecognized opcode %i\n", opcode);
    }

    if (LLVMIsABinaryOperator(instruction)) {
        printf("type: binary operator\n");
    }

    int n_operands = LLVMGetNumOperands(instruction);

    for (int i = 0; i < n_operands; i++) {
        printf("\noperand %i: ", i + 1);
        LLVMValueRef op = LLVMGetOperand(instruction, i);
        if (LLVMIsAConstant(op)) {
            printf("constant\n");
        } else {
            printf("not a constant\n");
        }

        // Print operand type
        LLVMValueKind operand_type = LLVMGetValueKind(op);
        switch (operand_type) {
            case LLVMConstantExprValueKind:
                printf("type = constant expression\n");
                break;
            case LLVMConstantIntValueKind:
                printf("type = integer\n");
                break;
            case LLVMFunctionValueKind:
                printf("type = function\n");
                break;
            case LLVMInstructionValueKind :
                printf("type = instruction\n");
                break;
            default:
                printf("unrecognized operand type %i\n", operand_type);
        }

        // Print operand value
        printf("value = %s\n", LLVMPrintValueToString(op));
    }
}

int main(const int argc, const char *const argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: llvm-parser inputfile.bc\n");
        return 1;
    }

    const char *const infile = argv[1];

    LLVMMemoryBufferRef memoryBuffer;
    // this should be allocated right? docs from LLVMCreateMemoryBuff..
    // aren't great?
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
        printf("\nloop through function\n");

        // loop through basic blocks
        for (LLVMBasicBlockRef block = LLVMGetFirstBasicBlock(fun);
             block; block = LLVMGetNextBasicBlock(block)) {
                printf("\nloop through block\n");

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
