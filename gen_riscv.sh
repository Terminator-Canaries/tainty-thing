#!/bin/bash

IFS='.'
read -ra file <<< "$1"

clang -c -fno-asynchronous-unwind-tables -emit-llvm "$1" -o "${file[0]}.bc"
llc -regalloc=basic -march=riscv32 -O3 "${file[0]}.bc" --frame-pointer=none
