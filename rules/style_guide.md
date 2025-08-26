# NASA C Style Guide - Flight Dynamics Division

## Overview
This style guide provides additional coding standards beyond the Power of 10 rules, focusing on readability, maintainability, and safety for NASA flight software.

## Naming Conventions

### Variables and Functions
**Rule**: Use descriptive names that clearly indicate purpose
**Compliant Examples**:
```c
int sensor_temperature;
int calculate_thrust_vector();
void initialize_guidance_system();
```

**Non-Compliant Examples**:
```c
int temp;
int calc();
void init();
```

### Constants and Macros
**Rule**: Use UPPER_CASE for constants, descriptive names
**Compliant Examples**:
```c
#define MAX_THRUST_LEVEL 1000
#define MIN_FUEL_THRESHOLD 50
const int MAX_ITERATION_COUNT = 1000;
```

**Non-Compliant Examples**:
```c
#define MAX 1000
#define MIN 50
const int max = 1000;
```

### Type Definitions
**Rule**: Use descriptive type names ending with `_t`
**Compliant Examples**:
```c
typedef struct {
    double x, y, z;
} position_vector_t;

typedef enum {
    SYSTEM_READY,
    SYSTEM_ACTIVE,
    SYSTEM_ERROR
} system_state_t;
```

## Code Structure

### Function Length
**Rule**: Functions should not exceed 50 lines
**Compliant Example**:
```c
int validate_sensor_data(sensor_data_t* data) {
    int validation_result = VALIDATION_PASS;
    
    if (data == NULL) {
        validation_result = VALIDATION_FAIL_NULL_POINTER;
    } else if (data->temperature < MIN_TEMPERATURE) {
        validation_result = VALIDATION_FAIL_LOW_TEMPERATURE;
    } else if (data->temperature > MAX_TEMPERATURE) {
        validation_result = VALIDATION_FAIL_HIGH_TEMPERATURE;
    }
    
    return validation_result;
}
```

### Comment Requirements
**Rule**: Every function must have a header comment explaining purpose, parameters, and return value
**Compliant Example**:
```c
/**
 * @brief Validates sensor data against operational limits
 * @param data Pointer to sensor data structure
 * @return Validation result code (VALIDATION_PASS or error code)
 * @note This function performs bounds checking on temperature values
 */
int validate_sensor_data(sensor_data_t* data);
```

### Error Handling
**Rule**: All functions must return error codes, never use global error variables
**Compliant Example**:
```c
typedef enum {
    SUCCESS = 0,
    ERROR_NULL_POINTER = -1,
    ERROR_INVALID_PARAMETER = -2,
    ERROR_SYSTEM_FAILURE = -3
} error_code_t;

error_code_t process_telemetry(telemetry_data_t* data) {
    if (data == NULL) {
        return ERROR_NULL_POINTER;
    }
    
    if (data->timestamp < 0) {
        return ERROR_INVALID_PARAMETER;
    }
    
    // Process data...
    return SUCCESS;
}
```

## Data Types and Safety

### Integer Types
**Rule**: Use explicit integer types with size guarantees
**Compliant Examples**:
```c
#include <stdint.h>

uint32_t sensor_id;
int16_t temperature;
uint8_t status_flags;
```

**Non-Compliant Examples**:
```c
int sensor_id;        // Size not guaranteed
short temperature;     // Size not guaranteed
char status_flags;    // Signed vs unsigned unclear
```

### Floating Point
**Rule**: Use `double` for calculations, `float` only for storage when memory is critical
**Compliant Example**:
```c
double calculate_trajectory(double initial_velocity, double angle) {
    double gravity = 9.80665;
    double range = (initial_velocity * initial_velocity * sin(2 * angle)) / gravity;
    return range;
}
```

### Array Bounds
**Rule**: Always check array bounds before access
**Compliant Example**:
```c
#define MAX_ARRAY_SIZE 100

int safe_array_access(int* array, int index) {
    if (array == NULL || index < 0 || index >= MAX_ARRAY_SIZE) {
        return ERROR_INVALID_PARAMETER;
    }
    return array[index];
}
```

## Control Structures

### If-Else Chains
**Rule**: Use `else if` for mutually exclusive conditions
**Compliant Example**:
```c
if (system_state == SYSTEM_READY) {
    initialize_system();
} else if (system_state == SYSTEM_ACTIVE) {
    continue_operation();
} else if (system_state == SYSTEM_ERROR) {
    handle_error();
} else {
    report_unknown_state();
}
```

### Switch Statements
**Rule**: Always include default case, use break statements
**Compliant Example**:
```c
switch (command) {
    case CMD_START:
        start_operation();
        break;
    case CMD_STOP:
        stop_operation();
        break;
    case CMD_RESET:
        reset_system();
        break;
    default:
        report_invalid_command(command);
        break;
}
```

## Memory and Resource Management

### Buffer Management
**Rule**: Use fixed-size buffers with explicit bounds checking
**Compliant Example**:
```c
#define BUFFER_SIZE 256

typedef struct {
    char data[BUFFER_SIZE];
    size_t length;
} buffer_t;

int add_to_buffer(buffer_t* buffer, const char* text) {
    if (buffer == NULL || text == NULL) {
        return ERROR_NULL_POINTER;
    }
    
    size_t text_length = strlen(text);
    if (buffer->length + text_length >= BUFFER_SIZE) {
        return ERROR_BUFFER_OVERFLOW;
    }
    
    strcpy(buffer->data + buffer->length, text);
    buffer->length += text_length;
    return SUCCESS;
}
```

### Resource Cleanup
**Rule**: Always clean up resources in reverse order of acquisition
**Compliant Example**:
```c
int process_with_resources() {
    resource_a_t* resource_a = acquire_resource_a();
    if (resource_a == NULL) {
        return ERROR_RESOURCE_ACQUISITION_FAILED;
    }
    
    resource_b_t* resource_b = acquire_resource_b();
    if (resource_b == NULL) {
        release_resource_a(resource_a);
        return ERROR_RESOURCE_ACQUISITION_FAILED;
    }
    
    // Process with resources...
    int result = perform_processing(resource_a, resource_b);
    
    // Cleanup in reverse order
    release_resource_b(resource_b);
    release_resource_a(resource_a);
    
    return result;
}
```

## ML Training Considerations

### Style Violation Patterns
- **Naming**: Short, non-descriptive names
- **Structure**: Long functions, missing comments
- **Types**: Implicit integer types, missing bounds checking
- **Control**: Missing default cases, improper error handling
- **Resources**: Missing cleanup, improper resource management

### Compliance Metrics
- **Function Length**: Track lines per function
- **Comment Coverage**: Measure documented functions
- **Error Handling**: Count functions with proper error codes
- **Type Safety**: Identify implicit type usage
- **Resource Management**: Check cleanup patterns

### Training Data Categories
1. **Naming Convention Examples**: Good vs. bad variable/function names
2. **Structure Examples**: Well-formed vs. poorly-formed functions
3. **Safety Examples**: Bounds checking, error handling patterns
4. **Resource Examples**: Proper vs. improper resource management
