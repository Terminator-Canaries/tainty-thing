project(taint-explosion)
cmake_minimum_required(VERSION 3.4.3)

# option to allow a user to specify where an LLVM install is on the system
set(LLVM_INSTALL_DIR "" CACHE STRING "An LLVM install directory.")

if("${LLVM_INSTALL_DIR}" STREQUAL "")
  message(FATAL_ERROR "LLVM_INSTALL_DIR not set! Set it to the location of an LLVM install.")
endif()

# fixup paths to only use the Linux convention
string(REPLACE "\\" "/" LLVM_INSTALL_DIR ${LLVM_INSTALL_DIR})

# tell CMake where LLVM's module is
list(APPEND CMAKE_MODULE_PATH ${LLVM_INSTALL_DIR}/lib/cmake/llvm)

# include LLVM
include(LLVMConfig)

add_executable(taint-explosion llvm-parser.c)

target_include_directories(taint-explosion PUBLIC ${LLVM_INCLUDE_DIRS})

target_link_libraries(taint-explosion PUBLIC LLVMBitReader LLVMBitWriter)

target_compile_options(taint-explosion PUBLIC
  $<$<C_COMPILER_ID:GNU>:-Wall -Wextra -Werror -std=gnu89>
  $<$<C_COMPILER_ID:Clang>:-Wall -Wextra -Werror -std=gnu99>
  $<$<C_COMPILER_ID:MSVC>:/Wall /WX /wd4514 /wd4710 /wd4820>)
