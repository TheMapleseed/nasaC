# The Power of 10: Rules for Developing Safety-Critical Code

## Overview
The Power of 10 rules were developed by Gerard J. Holzmann at NASA's Jet Propulsion Laboratory to eliminate C coding practices that complicate code review and static analysis for safety-critical systems.

## Core Rules

### Rule 1: Avoid Complex Flow Control
**Violation**: Use of `goto`, `setjmp()`, `longjmp()`, or recursion
**Compliant Alternative**: Use structured control flow with clear entry/exit points

**Example (Non-Compliant)**:
```c
void process_data() {
    if (error_condition) {
        goto cleanup;
    }
    // ... processing code
cleanup:
    // cleanup code
}
```

**Example (Compliant)**:
```c
void process_data() {
    if (error_condition) {
        cleanup();
        return;
    }
    // ... processing code
    cleanup();
}
```

### Rule 2: All Loops Must Have Fixed Upper Bounds
**Violation**: Loops without compile-time determinable upper bounds
**Compliant Alternative**: Use bounded loops with explicit limits

**Example (Non-Compliant)**:
```c
while (condition) {
    // loop body
}
```

**Example (Compliant)**:
```c
#define MAX_ITERATIONS 1000
int iteration_count = 0;
while (condition && iteration_count < MAX_ITERATIONS) {
    // loop body
    iteration_count++;
}
```

### Rule 3: Avoid Dynamic Memory Allocation
**Violation**: Use of `malloc()`, `free()`, or dynamic memory allocation
**Compliant Alternative**: Use static allocation or stack-based allocation

**Example (Non-Compliant)**:
```c
int* buffer = malloc(size * sizeof(int));
// ... use buffer
free(buffer);
```

**Example (Compliant)**:
```c
#define MAX_BUFFER_SIZE 1024
int buffer[MAX_BUFFER_SIZE];
// ... use buffer
```

### Rule 4: No Function Calls with More Than 2 Arguments
**Violation**: Functions with more than 2 parameters
**Compliant Alternative**: Use structures to group related parameters

**Example (Non-Compliant)**:
```c
int process_data(int x, int y, int z, int w, int v) {
    return x + y + z + w + v;
}
```

**Example (Compliant)**:
```c
typedef struct {
    int x, y, z, w, v;
} data_params_t;

int process_data(data_params_t params) {
    return params.x + params.y + params.z + params.w + params.v;
}
```

### Rule 5: Avoid Pointer Dereferencing More Than 2 Levels
**Violation**: Multiple levels of pointer indirection
**Compliant Alternative**: Use direct access or limit indirection levels

**Example (Non-Compliant)**:
```c
int value = ***ptr;
```

**Example (Compliant)**:
```c
int value = *ptr;
```

### Rule 6: All Variables Must Be Declared at the Top of Their Scope
**Violation**: Variable declarations mixed with executable code
**Compliant Alternative**: Declare all variables at scope beginning

**Example (Non-Compliant)**:
```c
void function() {
    int x = 5;
    // ... some code
    int y = 10;  // Declaration in middle of function
}
```

**Example (Compliant)**:
```c
void function() {
    int x;
    int y;
    
    x = 5;
    // ... some code
    y = 10;
}
```

### Rule 7: All Functions Must Have a Single Return Point
**Violation**: Multiple return statements in a function
**Compliant Alternative**: Use a single return at the end

**Example (Non-Compliant)**:
```c
int validate_input(int value) {
    if (value < 0) {
        return -1;
    }
    if (value > 100) {
        return -2;
    }
    return 0;
}
```

**Example (Compliant)**:
```c
int validate_input(int value) {
    int result = 0;
    
    if (value < 0) {
        result = -1;
    } else if (value > 100) {
        result = -2;
    }
    
    return result;
}
```

### Rule 8: No Use of Preprocessor Directives Except #include
**Violation**: Use of `#define`, `#ifdef`, `#ifndef`, etc.
**Compliant Alternative**: Use constants and conditional compilation sparingly

**Example (Non-Compliant)**:
```c
#define MAX_SIZE 100
#ifdef DEBUG
    printf("Debug info\n");
#endif
```

**Example (Compliant)**:
```c
const int MAX_SIZE = 100;
// Debug information handled through configuration
```

### Rule 9: No Use of Assignments in Expressions
**Violation**: Assignment operators within conditional expressions
**Compliant Alternative**: Separate assignment from condition checking

**Example (Non-Compliant)**:
```c
while ((ch = getchar()) != EOF) {
    // process character
}
```

**Example (Compliant)**:
```c
ch = getchar();
while (ch != EOF) {
    // process character
    ch = getchar();
}
```

### Rule 10: No Use of Multiple Assignments
**Violation**: Multiple assignments in a single statement
**Compliant Alternative**: Use separate assignment statements

**Example (Non-Compliant)**:
```c
a = b = c = 0;
```

**Example (Compliant)**:
```c
a = 0;
b = 0;
c = 0;
```

## ML Training Considerations

### Rule Violation Patterns
- **Flow Control**: Look for `goto`, recursion, complex loops
- **Memory Management**: Identify dynamic allocation calls
- **Function Design**: Count parameters, identify multiple returns
- **Variable Usage**: Check declaration placement and scope
- **Expression Complexity**: Find embedded assignments and multiple assignments

### Compliance Scoring
Each rule violation contributes to a compliance score:
- **Fully Compliant**: 0 violations
- **Minor Issues**: 1-2 violations
- **Moderate Issues**: 3-5 violations
- **Major Issues**: 6+ violations

### Training Data Generation
- Generate synthetic code samples with known violations
- Use static analysis tools to identify real violations
- Create paired examples (compliant vs. non-compliant)
- Tag each violation with specific rule numbers
