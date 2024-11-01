// advanced_macro_example.c

#include <stdio.h>

#pragma wave trace(enable)

// Simple value macros
#define PI 3.14159
#define MAX_CAPACITY 256

// Function-like macros
#define SQUARE(x) ((x) * (x))                   // Expects an integer or float
#define TRIPLE(x) ((x) * 3)                     // Expects an integer or float
#define ADD_ONE(x) ((x) + 1)                    // Expects an integer

// Nested macros for combining values
#define CONCAT(x, y) x ## y                     // Concatenates two tokens
#define TO_STR(x) #x                            // Converts to string
#define MAKE_UNIQUE_VAR(prefix, num) CONCAT(prefix, num)  // Creates identifiers like var1, var2

// Double-nested macro example for transformation
#define DOUBLE_AND_SQUARE(x) SQUARE(TRIPLE(x))  // Multiplies by 3, then squares the result



int main(void) {
    // Simple macro usage
    printf("Value of PI: %f\n", PI);
    printf("Max capacity: %d\n", MAX_CAPACITY);

    // Using nested function-like macros
    int num = 2;
    int result_square = SQUARE(num);
    int result_triple = TRIPLE(num);
    int result_add_one = ADD_ONE(num);

    printf("Square of %d: %d\n", num, result_square);
    printf("Triple of %d: %d\n", num, result_triple);
    printf("Add one to %d: %d\n", num, result_add_one);

    // Using double-nested macros
    int result_double_and_square = DOUBLE_AND_SQUARE(num);  // ((2 * 3) ^ 2) = 36
    printf("Double and square of %d: %d\n", num, result_double_and_square);

    // Using nested macros to create unique variable names
    int MAKE_UNIQUE_VAR(myVar, 1) = 100;  // Expands to int myVar1 = 100;
    printf("Generated variable myVar1: %d\n", myVar1);

    return 0;
}
