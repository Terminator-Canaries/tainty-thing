; ModuleID = 'testprogram2.c'
source_filename = "testprogram2.c"
target datalayout = "e-m:o-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-apple-macosx10.13.0"

@.str = private unnamed_addr constant [35 x i8] c"Usage: ./testprogram <arg1> <arg2>\00", align 1
@.str.1 = private unnamed_addr constant [17 x i8] c"TerminatorCanary\00", align 1

; Function Attrs: noinline nounwind optnone ssp uwtable
define i32 @main(i32, i8**) #0 {
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = alloca i8**, align 8
  %6 = alloca i32, align 4
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  %9 = alloca i32, align 4
  %10 = alloca i8*, align 8
  %11 = alloca i32, align 4
  %12 = alloca i32, align 4
  %13 = alloca i32, align 4
  store i32 0, i32* %3, align 4
  store i32 %0, i32* %4, align 4
  store i8** %1, i8*** %5, align 8
  %14 = load i32, i32* %4, align 4
  %15 = icmp ne i32 %14, 3
  br i1 %15, label %16, label %18

16:                                               ; preds = %2
  %17 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([35 x i8], [35 x i8]* @.str, i64 0, i64 0))
  call void @exit(i32 1) #3
  unreachable

18:                                               ; preds = %2
  %19 = load i8**, i8*** %5, align 8
  %20 = getelementptr inbounds i8*, i8** %19, i64 1
  %21 = load i8*, i8** %20, align 8
  %22 = call i32 @atoi(i8* %21)
  store i32 %22, i32* %6, align 4
  %23 = load i8**, i8*** %5, align 8
  %24 = getelementptr inbounds i8*, i8** %23, i64 2
  %25 = load i8*, i8** %24, align 8
  %26 = call i32 @atoi(i8* %25)
  store i32 %26, i32* %7, align 4
  %27 = call i32 @get_phone_location()
  store i32 %27, i32* %8, align 4
  %28 = call i32 @get_IMEI()
  store i32 %28, i32* %9, align 4
  %29 = call i8* @get_apple_ID()
  store i8* %29, i8** %10, align 8
  %30 = load i32, i32* %6, align 4
  %31 = icmp slt i32 %30, 0
  br i1 %31, label %32, label %33

32:                                               ; preds = %18
  store i32 0, i32* %3, align 4
  br label %50

33:                                               ; preds = %18
  %34 = load i32, i32* %6, align 4
  %35 = icmp eq i32 %34, 0
  br i1 %35, label %36, label %38

36:                                               ; preds = %33
  %37 = load i32, i32* %7, align 4
  store i32 %37, i32* %3, align 4
  br label %50

38:                                               ; preds = %33
  br label %39

39:                                               ; preds = %38
  %40 = load i32, i32* %6, align 4
  %41 = load i32, i32* %7, align 4
  %42 = add nsw i32 %40, %41
  store i32 %42, i32* %11, align 4
  %43 = load i32, i32* %11, align 4
  %44 = load i32, i32* %8, align 4
  %45 = sub nsw i32 %43, %44
  store i32 %45, i32* %12, align 4
  %46 = load i32, i32* %9, align 4
  %47 = load i32, i32* %12, align 4
  %48 = srem i32 %46, %47
  store i32 %48, i32* %13, align 4
  %49 = load i32, i32* %13, align 4
  store i32 %49, i32* %3, align 4
  br label %50

50:                                               ; preds = %39, %36, %32
  %51 = load i32, i32* %3, align 4
  ret i32 %51
}

declare i32 @printf(i8*, ...) #1

; Function Attrs: noreturn
declare void @exit(i32) #2

declare i32 @atoi(i8*) #1

; Function Attrs: noinline nounwind optnone ssp uwtable
define i32 @get_phone_location() #0 {
  ret i32 42
}

; Function Attrs: noinline nounwind optnone ssp uwtable
define i32 @get_IMEI() #0 {
  ret i32 12345678
}

; Function Attrs: noinline nounwind optnone ssp uwtable
define i8* @get_apple_ID() #0 {
  ret i8* getelementptr inbounds ([17 x i8], [17 x i8]* @.str.1, i64 0, i64 0)
}

attributes #0 = { noinline nounwind optnone ssp uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #2 = { noreturn "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #3 = { noreturn }

!llvm.module.flags = !{!0, !1}
!llvm.ident = !{!2}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"PIC Level", i32 2}
!2 = !{!"clang version 9.0.0 (tags/RELEASE_900/final)"}
