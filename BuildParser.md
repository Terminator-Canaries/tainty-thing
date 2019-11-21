`mkdir build`
`cd build/`
`cmake -DLLVM_INSTALL_DIR=/usr/local/opt/llvm ..`
`make`

Generate .ll file:
`clang -S -emit-llvm testprogram.c`

Generate .bc file:
`clang -c -emit-llvm testprogram.ll -o testprogram.bc`
