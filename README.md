# Tainty Thing

## Project Steps

Let's try to get step 1 working by next week 11/11. So that we have a sense of the difficulty and we can start asking questions like "what is the nature of the program that we will taint?" The inital interpreter can be very limited and just handle a few instructions, we just have to pull the pieces together. We're not dividing responsiblities yet, just try to see if you can get something to work and then share it.

1. Build a (limited) LLVM interpreter in Python.

	- Compile small C program to LLVM (e.g. helloworld.c)
	- Find a LLVM parser/iterator
	- Interpreter code could be in C, C++, or Python... mostly depends on parser/iterator

2. Tainting

	- count taint every X instructions initially

3. Snapshotting

	- Pickling to take snapshots [https://docs.python.org/3/library/pickle.html]()

4. Start small with steps 1-3 to see what works, then build them out more

5. Eventually - where is there explosion? how do we reduce explosion? what variables are problematic?

## LLVM Related Resources

LLVM Documentation - [https://llvm.org/docs/LangRef.html]()  

CMU "More on the LLVM Compiler"
[http://www.cs.cmu.edu/afs/cs/academic/class/15745-s15/public/lectures/L6-LLVM2-1up.pdf]()

More LLVM Overview/Tutorials  
[https://www.cs.cmu.edu/~janh/courses/411/17/lec/24-llvm-slides.pdf]()
[https://blog.regehr.org/archives/1605]()  
[http://releases.llvm.org/2.6/docs/tutorial/JITTutorial1.html]()

## Compiling helloworld.c to LLVM

Walkthrough of the `helloworld.ll` file

Generate with command:
`clang -S -emit-llvm helloworld.c`

Starts with module metadata:

	; ModuleID = 'helloworld.c'
	source_filename = "helloworld.c"
	target datalayout = "e-m:o-i64:64-f80:128-n8:16:32:64-S128"
	target triple = "x86_64-apple-macosx10.14.0"
	
Global declaration:

Declare the "Hello World\n" constant  
Save in a global variable `.str`  
`i8` char or byte 
`[13 x i8]` array of 13 chars/bytes
	
	@.str = private unnamed_addr constant [13 x i8] c"Hello world\0A\00", align 1
	
Define main function  
`i32 @main()` means main takes nothing, returns 4 byte int 

	; Function Attrs: noinline nounwind optnone ssp uwtable
	define i32 @main() #0 {
	
`alloca` [https://llvm.org/docs/LangRef.html#alloca-instruction]()  
`i32` = 32 bit integer  

* allocate a 4 byte integer
* store 0 in a pointer to that integer?
* call a function that returns a 4 byte int, takes a pointer to 1 byte values (char*), pass the `.str` into it


		%1 = alloca i32, align 4
		store i32 0, i32* %1, align 4
	  	%2 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([13 x i8], [13 x i8]* @.str, i32 0, i32 0))
	  
Return 0
	  
	  ret i32 0
	}
	
printf declared
	
	declare i32 @printf(i8*, ...) #1
	
Attributes and metadata
	
	attributes #0 = { noinline nounwind optnone ssp uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
	attributes #1 = { "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
	
	!llvm.module.flags = !{!0, !1, !2}
	!llvm.ident = !{!3}
	
	!0 = !{i32 2, !"SDK Version", [2 x i32] [i32 10, i32 14]}
	!1 = !{i32 1, !"wchar_size", i32 4}
	!2 = !{i32 7, !"PIC Level", i32 2}
	!3 = !{!"Apple clang version 11.0.0 (clang-1100.0.33.12)"}
	
