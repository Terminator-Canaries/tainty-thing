#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc != 3) {
        return 1;
    }
    int x = atoi(argv[1]);
    int y = atoi(argv[2]);
    if (x == 1) {
        return x + y;
    } else {
        return 0;
    }
}
