Checkout this branch:

    git clone git@github.com:Terminator-Canaries/tainty-thing.git taint-explosion
    git checkout -b mona origin/mona    

Generate .ll file:

    clang -S -emit-llvm testprogram.c

Generate .bc file:

    clang -c -emit-llvm testprogram.ll -o testprogram.bc

You must have llvm installed.
If your llvm is not at /usr/local/opt/llvm, replace this path with the
path to your llvm.

Setup build:

    mkdir build
    cd build/
    cmake -DLLVM_INSTALL_DIR=/usr/local/opt/llvm ..

Run parser:

    make
    ./taint-explosion ../testprogram.bc

References

LLVM C API docs:

https://llvm.org/doxygen/group__LLVMC.html (Core and BitReader mostly)

Parser example code and writeup:

http://www.duskborn.com/posts/optimizing-llvm-ir-from-the-c-api/

http://www.duskborn.com/posts/how-to-read-write-llvm-bitcode/

https://github.com/sheredom/llvm_bc_parsing_example
