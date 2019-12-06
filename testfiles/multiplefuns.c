int doSomething(int x) {
    if (x > 5) {
        return x;
    }
    return x + 1;
}

int main(int argc, char *argv[]) {
    if (argc > 3) {
        return doSomething(10);
    } else {
        for (int i = argc; i > 0; i--) {
            doSomething(i);
        }
    }
    return 0;
}
