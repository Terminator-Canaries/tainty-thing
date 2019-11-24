#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include <map>
#include <utility>

#include <llvm-c/Core.h>
#include <llvm-c/BitReader.h>
#include <llvm-c/BitWriter.h>

#define BUFSIZE 1000

using namespace std;

static map<long, int> labels;
static map<long, int> stupid_map;

void print_operand_info(FILE* f, LLVMValueRef instruction) {
    fprintf(f, "[");

    int n_operands = LLVMGetNumOperands(instruction);
    for (int i = 0; i < n_operands; i++) {
        fprintf(f, "{");
        LLVMValueRef op = LLVMGetOperand(instruction, i);
        LLVMValueRef constant = LLVMIsAConstant(op);
        if (constant) {
            fprintf(f, "\"isConstant\": true");
        } else {
            fprintf(f, "\"isConstant\": false");
            fprintf(f, ",\"register\": \"var-%i\"", labels[(long) op]);
        }

        // // Print operand type
        // LLVMTypeKind operand_type = LLVMGetTypeKind(op);
        // printf("%s\n", LLVMPrintTypeToString(operand_type));

        // LLVMConstInt ??

        // Print operand value
        LLVMValueKind value_kind = LLVMGetValueKind(op);
        fprintf(f, ",\"valueKind\":");
        switch (value_kind) {
            case LLVMArgumentValueKind:
                fprintf(f, "\"argument\"");
                break;
            case LLVMBasicBlockValueKind:
                fprintf(f, "\"basic block\"");
                fprintf(f, ",\"value\": \"block-%i\"", labels[(long) op]);
                break;
            case LLVMConstantExprValueKind:
                fprintf(f, "\"constant expression\"");
                break;
            case LLVMConstantIntValueKind:
                fprintf(f, "\"integer\"");
                fprintf(f, ",\"zero_extended_value\": %llu", LLVMConstIntGetZExtValue(op));
                fprintf(f, ",\"sign_extedned_value\": %llu", LLVMConstIntGetSExtValue(op));
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
        case LLVMGetElementPtr:
            fprintf(f, "\"get element ptr\"");
            break;
        default:
            fprintf(f, "\"unrecognized opcode %i\"", opcode);
    }

    if (opcode != LLVMStore) {
        labels.insert(pair<long, int>((long) instruction, labels.size()));
        fprintf(f, ",\"register\": \"var-%i\"", labels[(long) instruction]);
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

        LLVMBasicBlockRef firstBlock = LLVMGetFirstBasicBlock(fun);
        LLVMBasicBlockRef lastBlock = LLVMGetLastBasicBlock(fun);

        // Label blocks
        for (LLVMBasicBlockRef block = firstBlock; block;
            block = LLVMGetNextBasicBlock(block)) {
                labels.insert(pair<long, int>((long) block, labels.size()));
        }

        // Read instructions in each block
        for (LLVMBasicBlockRef block = firstBlock; block;
            block = LLVMGetNextBasicBlock(block)) {
                fprintf(f, "{\"block-%i\":[", labels[(long) block]);

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
