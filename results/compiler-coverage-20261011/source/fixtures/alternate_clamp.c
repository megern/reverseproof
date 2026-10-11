#include <stdio.h>
#include <stdlib.h>
#ifndef UPPER
#define UPPER 23
#endif
/* Owned alternate-source fixture: no external application is executed. */
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    long value = strtol(argv[1], NULL, 10);
#ifdef AFFINE
    long result = value + 1;
#else
    long result = value;
    if (result > UPPER) result = UPPER;
    if (result < 0) result = 0;
#endif
    printf("%ld\n", result);
    return 0;
}
