# NASA C Code Compliance Checklist

## Overview
This checklist provides a systematic approach for evaluating C code compliance with NASA standards. Each item can be used as a training target for machine learning models.

## Power of 10 Rules Compliance

### Rule 1: Flow Control
- [ ] No `goto` statements
- [ ] No `setjmp()` or `longjmp()` calls
- [ ] No recursive function calls
- [ ] All control flow is structured and predictable

**Violation Examples**:
```c
// VIOLATION: goto usage
void bad_function() {
    if (error) goto cleanup;
    // ... code ...
cleanup:
    return;
}

// VIOLATION: recursion
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);  // Recursive call
}
```

**Compliant Examples**:
```c
// COMPLIANT: structured control flow
void good_function() {
    if (error) {
        cleanup();
        return;
    }
    // ... code ...
    cleanup();
}

// COMPLIANT: iterative approach
int factorial(int n) {
    int result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}
```

### Rule 2: Loop Bounds
- [ ] All loops have compile-time determinable upper bounds
- [ ] No infinite loops
- [ ] Loop counters are properly bounded

**Violation Examples**:
```c
// VIOLATION: unbounded loop
while (condition) {
    // No upper bound guarantee
}

// VIOLATION: potential infinite loop
for (int i = 0; i < size; i++) {
    if (some_condition) {
        i--;  // Could cause infinite loop
    }
}
```

**Compliant Examples**:
```c
// COMPLIANT: bounded loop
#define MAX_ITERATIONS 1000
int count = 0;
while (condition && count < MAX_ITERATIONS) {
    // ... loop body ...
    count++;
}

// COMPLIANT: bounded for loop
for (int i = 0; i < MAX_SIZE && i < actual_size; i++) {
    // ... loop body ...
}
```

### Rule 3: Memory Allocation
- [ ] No `malloc()`, `calloc()`, `realloc()` calls
- [ ] No `free()` calls
- [ ] All memory is statically allocated or stack-based

**Violation Examples**:
```c
// VIOLATION: dynamic allocation
int* buffer = malloc(size * sizeof(int));
// ... use buffer ...
free(buffer);

// VIOLATION: dynamic allocation in loop
for (int i = 0; i < count; i++) {
    char* str = malloc(100);
    // ... use str ...
    free(str);
}
```

**Compliant Examples**:
```c
// COMPLIANT: static allocation
#define MAX_BUFFER_SIZE 1024
int buffer[MAX_BUFFER_SIZE];

// COMPLIANT: stack allocation
void function() {
    char local_buffer[256];
    // ... use local_buffer ...
}
```

### Rule 4: Function Parameters
- [ ] No functions with more than 2 parameters
- [ ] Use structures to group related parameters
- [ ] Parameter validation is performed

**Violation Examples**:
```c
// VIOLATION: too many parameters
int process_data(int x, int y, int z, int w, int v) {
    return x + y + z + w + v;
}

// VIOLATION: complex parameter list
void configure_system(int mode, int timeout, int retries, 
                     int buffer_size, int priority) {
    // ... implementation ...
}
```

**Compliant Examples**:
```c
// COMPLIANT: parameter structure
typedef struct {
    int x, y, z, w, v;
} data_params_t;

int process_data(data_params_t params) {
    return params.x + params.y + params.z + params.w + params.v;
}

// COMPLIANT: limited parameters
void configure_system(config_t config) {
    // ... implementation ...
}
```

### Rule 5: Pointer Dereferencing
- [ ] No more than 2 levels of pointer indirection
- [ ] Pointer validity is checked before use
- [ ] Null pointer checks are performed

**Violation Examples**:
```c
// VIOLATION: excessive indirection
int value = ***ptr;

// VIOLATION: no null check
int value = *ptr;  // Could crash if ptr is NULL
```

**Compliant Examples**:
```c
// COMPLIANT: limited indirection
int value = *ptr;

// COMPLIANT: with null check
int value = 0;
if (ptr != NULL) {
    value = *ptr;
}
```

### Rule 6: Variable Declarations
- [ ] All variables declared at scope beginning
- [ ] No variable declarations mixed with executable code
- [ ] Variables are properly initialized

**Violation Examples**:
```c
// VIOLATION: declaration in middle of function
void function() {
    int x = 5;
    // ... some code ...
    int y = 10;  // Declaration not at beginning
}

// VIOLATION: declaration in loop
for (int i = 0; i < 10; i++) {
    int temp = i * 2;  // Declaration in loop
}
```

**Compliant Examples**:
```c
// COMPLIANT: all declarations at beginning
void function() {
    int x;
    int y;
    
    x = 5;
    // ... some code ...
    y = 10;
}

// COMPLIANT: declaration outside loop
void function() {
    int temp;
    for (int i = 0; i < 10; i++) {
        temp = i * 2;
    }
}
```

### Rule 7: Function Returns
- [ ] Single return point per function
- [ ] Return value is properly set
- [ ] Error conditions are handled consistently

**Violation Examples**:
```c
// VIOLATION: multiple return points
int validate(int value) {
    if (value < 0) return -1;
    if (value > 100) return -2;
    return 0;
}

// VIOLATION: inconsistent return handling
int process(int value) {
    if (value < 0) return ERROR;
    // ... processing ...
    if (success) return SUCCESS;
    // Missing return for failure case
}
```

**Compliant Examples**:
```c
// COMPLIANT: single return point
int validate(int value) {
    int result = 0;
    
    if (value < 0) {
        result = -1;
    } else if (value > 100) {
        result = -2;
    }
    
    return result;
}

// COMPLIANT: consistent return handling
int process(int value) {
    int result = ERROR;
    
    if (value >= 0) {
        // ... processing ...
        if (success) {
            result = SUCCESS;
        }
    }
    
    return result;
}
```

### Rule 8: Preprocessor Usage
- [ ] Only `#include` directives allowed
- [ ] No `#define` for constants
- [ ] No conditional compilation directives
- [ ] No macro definitions

**Violation Examples**:
```c
// VIOLATION: constant definition
#define MAX_SIZE 100

// VIOLATION: conditional compilation
#ifdef DEBUG
    printf("Debug info\n");
#endif

// VIOLATION: macro definition
#define SQUARE(x) ((x) * (x))
```

**Compliant Examples**:
```c
// COMPLIANT: const declaration
const int MAX_SIZE = 100;

// COMPLIANT: configuration-based debugging
if (debug_enabled) {
    printf("Debug info\n");
}

// COMPLIANT: inline function
static inline int square(int x) {
    return x * x;
}
```

### Rule 9: Assignment in Expressions
- [ ] No assignment operators in conditional expressions
- [ ] No assignment operators in function calls
- [ ] Assignments are separate from condition checking

**Violation Examples**:
```c
// VIOLATION: assignment in condition
while ((ch = getchar()) != EOF) {
    // ... process character ...
}

// VIOLATION: assignment in function call
if (process_data(value = 5)) {
    // ... handle success ...
}
```

**Compliant Examples**:
```c
// COMPLIANT: separate assignment
ch = getchar();
while (ch != EOF) {
    // ... process character ...
    ch = getchar();
}

// COMPLIANT: separate assignment
value = 5;
if (process_data(value)) {
    // ... handle success ...
}
```

### Rule 10: Multiple Assignments
- [ ] No multiple assignments in single statement
- [ ] Each assignment is on separate line
- [ ] Assignment order is clear and predictable

**Violation Examples**:
```c
// VIOLATION: multiple assignments
a = b = c = 0;

// VIOLATION: complex assignment chain
result = (temp = (value = 5) + 3) * 2;
```

**Compliant Examples**:
```c
// COMPLIANT: separate assignments
a = 0;
b = 0;
c = 0;

// COMPLIANT: clear assignment order
value = 5;
temp = value + 3;
result = temp * 2;
```

## Style Guide Compliance

### Naming Conventions
- [ ] Variables use descriptive names
- [ ] Functions use descriptive names
- [ ] Constants use UPPER_CASE
- [ ] Types end with `_t`

### Code Structure
- [ ] Functions are under 50 lines
- [ ] Functions have header comments
- [ ] Error handling is consistent
- [ ] Resource cleanup is proper

### Data Safety
- [ ] Explicit integer types used
- [ ] Array bounds are checked
- [ ] Null pointers are validated
- [ ] Floating point precision is appropriate

## ML Training Implementation

### Compliance Scoring Algorithm
```python
def calculate_compliance_score(code_analysis):
    score = 100
    
    # Power of 10 rules (70 points)
    for rule in power_of_10_rules:
        if rule.violated:
            score -= rule.penalty
    
    # Style guide rules (30 points)
    for rule in style_rules:
        if rule.violated:
            score -= rule.penalty
    
    return max(0, score)
```

### Training Data Structure
```json
{
    "code_sample": "int main() { return 0; }",
    "compliance_score": 95,
    "violations": [
        {
            "rule": "rule_6",
            "description": "Missing variable declarations at scope beginning",
            "severity": "minor"
        }
    ],
    "annotations": {
        "function_count": 1,
        "line_count": 1,
        "complexity_score": 1
    }
}
```

### Automated Compliance Checking
1. **Static Analysis**: Use tools like cppcheck, clang-tidy
2. **Pattern Matching**: Regular expressions for common violations
3. **AST Analysis**: Parse code and analyze structure
4. **Rule Validation**: Apply each rule systematically
5. **Score Calculation**: Compute overall compliance score
