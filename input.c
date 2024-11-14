#pragma wave trace(enable)
#include <stdio.h>
#include <stdint.h>

#define PI 3.14159
#define MAX_CAPACITY 256
#define MIN_CAPACITY (MAX_CAPACITY >> 4)

// Function-like macros
#define SQUARE(x) ((x) * (x))                   // Expects an integer or float
#define TRIPLE(x) ((x) * 3)                     // Expects an integer or float
#define ADD_ONE(x) ((x) + 1)                    // Expects an integer

#define INDIRECT_SQUARE(x) ((*(x)) * (*(x)))        // Expects an int* or float*

#define INDEX(x, y) (*(x + y))

// Nested macros for combining values
#define CONCAT(x, y) x ## y                     // Concatenates two tokens
#define TO_STR(x) #x                            // Converts to string
#define MAKE_UNIQUE_VAR(prefix, num) CONCAT(prefix, num)  // Creates identifiers like var1, var2

// Double-nested macro example for transformation
#define TRIPLE_AND_SQUARE(x) SQUARE(TRIPLE(x))  // Multiplies by 3, then squares the result

int main(void) {
    // Simple macro usage
    printf("Value of PI: %f\n", PI);
    printf("Max capacity: %d\n", MAX_CAPACITY);
    printf("Min capacity: %d\n", MIN_CAPACITY);

    uint64_t bruh = MIN_CAPACITY;

    float test[4] = { 1.1, 6.2, 9.3, 4.4 };
    float hmm = INDEX(test, 2);
    char aahhhhhh = (SQUARE(hmm) == INDIRECT_SQUARE(test + 2));

    printf("3rd value of Test: %f\n", hmm);
    printf("Indirect Square %s\n", aahhhhhh ? "works" : "doesn't work");

    // Using nested function-like macros
    int num = 2;
    int result_square = SQUARE(num) + SQUARE(0x5032L);
    float f_square = SQUARE(7.27);
    int result_triple = TRIPLE(num);
    int result_add_one = ADD_ONE(num);

    printf("Square of %d: %d\n", num, result_square);
    printf("Triple of %d: %d\n", num, result_triple);
    printf("Add one to %d: %d\n", num, result_add_one);

    // Using double-nested macros
    double result_triple_and_square = TRIPLE_AND_SQUARE(PI);  // ((2 * 3) ^ 2) = 36
    printf("Triple and square of %f: %lf\n", PI, result_triple_and_square);

    // Using nested macros to create unique variable names
    int MAKE_UNIQUE_VAR(myVar, 1) = 100;  // Expands to int myVar1 = 100;
    printf("Generated variable myVar1: %d\n", myVar1);

    return 0;
}
