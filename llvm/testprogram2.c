  
#include <stdio.h>
#include <stdlib.h>

int get_location();

int get_IMEI();

char* get_apple_ID();

int main(int argc, char **argv) {
    if (argc != 3) {
        printf("Usage: ./testprogram <arg1> <arg2>");
        exit(1);
    }

    int arg1 = atoi(argv[1]);
    int arg2 = atoi(argv[2]);

    int location = get_location();
    int IMEI = get_IMEI();
    char* appleID = get_apple_ID();

    if (arg1 < 0) {
        return 0;
    } 
    else if (arg1 == 0) {
        return arg2;
    }

    int x = arg1 + arg2;
    int y = x - location;
    int z = IMEI % y;
    
    return z;
}

int get_location() {
    return 42;
}

int get_IMEI() {
    return 12345678;
}

char* get_apple_ID() {
    return "TerminatorCanary";
}