#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include <llvm-c/Core.h>
#include <llvm-c/BitReader.h>
#include <llvm-c/BitWriter.h>

#define BUFSIZE 1000

void print_operand_info(FILE* f, LLVMValueRef instruction) {
    fprintf(f, "[");

    int n_operands = LLVMGetNumOperands(instruction);
    for (int i = 0; i < n_operands; i++) {
        fprintf(f, "{");
        LLVMValueRef op = LLVMGetOperand(instruction, i);
        if (LLVMIsAConstant(op)) {
            fprintf(f, "\"isConstant\": true");
        } else {
            fprintf(f, "\"isConstant\": false");
        }

        // // Print operand type
        // LLVMTypeKind operand_type = LLVMGetTypeKind(op);
        // printf("%s\n", LLVMPrintTypeToString(operand_type));

        // Print operand value
        LLVMValueKind value_kind = LLVMGetValueKind(op);
        fprintf(f, ",\"valueKind\":");
        switch (value_kind) {
            case LLVMConstantExprValueKind:
                fprintf(f, "\"constant expression\"");
                break;
            case LLVMConstantIntValueKind:
                fprintf(f, "\"integer\"");
                break;
            case LLVMFunctionValueKind:
                fprintf(f, "\"function\"");
                break;
            case LLVMInstructionValueKind :
                fprintf(f, "\"instruction\"");
                break;
            default:
                fprintf(f, "\"unrecognized value kind %i\"", value_kind);
        }

        // // Print operand value
        // printf("value = %s\n", LLVMPrintValueToString(op));
        fprintf(f, "}");
        if (i < n_operands - 1) {
            fprintf(f, ",");
        }
    }
    fprintf(f, "]");
}

void print_instruction_info(FILE* f, LLVMValueRef instruction) {
    fprintf(f, "{");

    // Get the opcode for this instruction
    // There are many more, only handling a few cases here for example
    fprintf(f, "\"opcode\":");
    LLVMOpcode opcode = LLVMGetInstructionOpcode(instruction);
    switch (opcode) {
        case LLVMBr:
            fprintf(f,"\"br\"");
            break;
        case LLVMRet:
            fprintf(f, "\"ret\"");
            break;
        case LLVMAdd:
            fprintf(f, "\"add\"");
            break;
        case LLVMLoad:
            fprintf(f, "\"load\"");
            break;
        case LLVMAlloca:
            fprintf(f, "\"alloca\"");
            break;
        case LLVMStore:
            fprintf(f, "\"store\"");
            break;
        case LLVMCall:
            fprintf(f, "\"call\"");
            break;
        case LLVMICmp:
            fprintf(f, "\"icmp\"");
            break;
        default:
            fprintf(f, "\"unrecognized opcode %i\"", opcode);
    }
    fprintf(f, ",\"operands\":");
    print_operand_info(f, instruction);
    fprintf(f, "}");
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

    // Open file to write json representation to
    FILE* f = fopen("../output.json", "w");
    fprintf(f, "{\"functions\":[");

    // loop through functions
    LLVMValueRef firstFun = LLVMGetFirstFunction(module);
    LLVMValueRef lastFun = LLVMGetLastFunction(module);
    for (LLVMValueRef fun = firstFun; fun; fun = LLVMGetNextFunction(fun)) {
        fprintf(f, "{\"blocks\":[");

        // loop through basic blocks
        LLVMBasicBlockRef firstBlock = LLVMGetFirstBasicBlock(fun);
        LLVMBasicBlockRef lastBlock = LLVMGetLastBasicBlock(fun);
        for (LLVMBasicBlockRef block = firstBlock; block;
            block = LLVMGetNextBasicBlock(block)) {
                fprintf(f, "{\"label%s\":[", LLVMGetBasicBlockName(block));

                // loop through instructions
                LLVMValueRef firstInstr = LLVMGetFirstInstruction(block);
                LLVMValueRef lastInstr = LLVMGetLastInstruction(block);
                for (LLVMValueRef instr = firstInstr; instr;
                    instr = LLVMGetNextInstruction(instr)) {
                        print_instruction_info(f, instr);
                        if (instr != lastInstr) {
                            fprintf(f, ",");
                        }
                    }

                fprintf(f, "]}");
                if (block != lastBlock) {
                    fprintf(f, ",");
                }
            }

            fprintf(f, "]}");
            if (fun != lastFun) {
                fprintf(f, ",");
            }
    }

    fprintf(f, "]}");

    LLVMDisposeModule(module);
    fclose(f);

    return 0;
}
