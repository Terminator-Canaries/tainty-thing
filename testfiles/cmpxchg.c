#include <stdio.h>
#include <stdlib.h>

// correct taint behavior for this should be,
int cmpxchg(int *a, int *b, int *c) {
  // taint(a) = taint(b)
  // because the value of a is fully dependent on the value of b
  if (*a == *b) {
    // in this case,
    // taint(b) = taint(c)
    *b = *c;
  } else {
    *a = *b;
  }
}

int main(int argc, char *argv[]) {
  if (argc != 3) {
    return 1;
  } else {
    int a = argv[0];
    int b = argv[1];
    int c = argv[2];
    cmpxchg(&a, &b, &c);
    return 0;
  }
}
