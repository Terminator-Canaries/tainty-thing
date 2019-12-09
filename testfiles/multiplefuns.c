int doSomething(int x) {
  if (x > 5) {
    return x;
  }
  return x + 1;
}

int get_user_location() { return 1308481230; }

int main(int argc, char *argv[]) {
  int a = get_user_location();
  if (argc > 3) {
    return doSomething(a);
  } else {
    for (int i = argc; i > 0; i--) {
      doSomething(i);
    }
  }
  return 0;
}
