; ModuleID = 'testprogram.c'
source_filename = "testprogram.c"
target datalayout = "e-m:o-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-apple-macosx10.13.0"

; Function Attrs: noinline nounwind optnone ssp uwtable
define i32 @main(i32, i8**) #0 {
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = alloca i8**, align 8
  %6 = alloca i32, align 4
  %7 = alloca i32, align 4
  store i32 0, i32* %3, align 4
  store i32 %0, i32* %4, align 4
  store i8** %1, i8*** %5, align 8
  %8 = load i32, i32* %4, align 4
  %9 = icmp ne i32 %8, 3
  br i1 %9, label %10, label %11

10:                                               ; preds = %2
  store i32 1, i32* %3, align 4
  br label %27

11:                                               ; preds = %2
  %12 = load i8**, i8*** %5, align 8
  %13 = getelementptr inbounds i8*, i8** %12, i64 1
  %14 = load i8*, i8** %13, align 8
  %15 = call i32 @atoi(i8* %14)
  store i32 %15, i32* %6, align 4
  %16 = load i8**, i8*** %5, align 8
  %17 = getelementptr inbounds i8*, i8** %16, i64 2
  %18 = load i8*, i8** %17, align 8
  %19 = call i32 @atoi(i8* %18)
  store i32 %19, i32* %7, align 4
  %20 = load i32, i32* %6, align 4
  %21 = icmp eq i32 %20, 1
  br i1 %21, label %22, label %26

22:                                               ; preds = %11
  %23 = load i32, i32* %6, align 4
  %24 = load i32, i32* %7, align 4
  %25 = add nsw i32 %23, %24
  store i32 %25, i32* %3, align 4
  br label %27

26:                                               ; preds = %11
  store i32 0, i32* %3, align 4
  br label %27

27:                                               ; preds = %26, %22, %10
  %28 = load i32, i32* %3, align 4
  ret i32 %28
}

declare i32 @atoi(i8*) #1

attributes #0 = { noinline nounwind optnone ssp uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }

!llvm.module.flags = !{!0, !1}
!llvm.ident = !{!2}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"PIC Level", i32 2}
!2 = !{!"clang version 9.0.0 (tags/RELEASE_900/final)"}
