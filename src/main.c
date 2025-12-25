#include <stdio.h>

/* Utility functions */
int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}

int square(int x) {
    return multiply(x, x);
}

/* Computational kernels */
int compute_series(int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum = add(sum, square(i));
    }
    return sum;
}

int compute_product(int n) {
    int prod = 1;
    for (int i = 1; i <= n; i++) {
        prod = multiply(prod, i);
    }
    return prod;
}

/* Helper functions */
int helper_A(int x) {
    return add(x, 10);
}

int helper_B(int x) {
    return helper_A(x) + square(x);
}

/* Dispatcher function */
int process(int mode, int value) {
    if (mode == 0) {
        return compute_series(value);
    } else if (mode == 1) {
        return compute_product(value);
    } else {
        return helper_B(value);
    }
}

/* Cyclic calls */
int cycle_1(int x);
int cycle_2(int x);

int cycle_1(int x) {
    if (x <= 0) return x;
    return cycle_2(x - 1);
}

int cycle_2(int x) {
    return cycle_1(x - 1);
}

/* Dead code */
int unused_function(int x) {
    return x * 42;
}

/* Entry point */
int main() {
    int result1 = process(0, 1000);
    int result2 = process(1, 10);
    int result3 = process(2, 5);

    cycle_1(5);

    printf("%d %d %d\n", result1, result2, result3);
    return 0;
}
