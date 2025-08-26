# NASA C Code Compliance - Resource Management & Oversubscription Guidelines

## Overview

This document provides comprehensive coverage of **resource management patterns** and **oversubscription handling** required for NASA safety-critical aerospace systems. It ensures robust resource utilization, safety margins, and graceful degradation under resource constraints.

## NASA Resource Management Requirements

### 1. Resource Margins

#### Safety Margin Definitions
```c
#include <stdint.h>
#include <stdbool.h>

/* NASA-compliant resource margin definitions */
#define RESOURCE_SAFETY_MARGIN_PERCENT    20U    /* 20% safety margin */
#define RESOURCE_WARNING_THRESHOLD_PERCENT 70U    /* Warning at 70% usage */
#define RESOURCE_CRITICAL_THRESHOLD_PERCENT 85U   /* Critical at 85% usage */
#define RESOURCE_EMERGENCY_THRESHOLD_PERCENT 95U  /* Emergency at 95% usage */

/* Resource margin structure */
typedef struct {
    uint32_t total_capacity;      /* Total resource capacity */
    uint32_t current_usage;       /* Current resource usage */
    uint32_t safety_margin;       /* Calculated safety margin */
    uint32_t warning_threshold;   /* Warning threshold value */
    uint32_t critical_threshold;  /* Critical threshold value */
    uint32_t emergency_threshold; /* Emergency threshold value */
    bool margin_violation;        /* Safety margin violation flag */
} nasa_resource_margins_t;

/* NASA-compliant resource margin calculation */
nasa_result_t nasa_calculate_resource_margins(
    nasa_resource_margins_t* margins,
    uint32_t total_capacity
) {
    if (margins == NULL) {
        return NASA_ERROR_INVALID_PARAMETER;
    }
    
    if (total_capacity == 0U) {
        return NASA_ERROR_INVALID_PARAMETER;
    }
    
    /* Calculate safety margins */
    margins->total_capacity = total_capacity;
    margins->safety_margin = (total_capacity * RESOURCE_SAFETY_MARGIN_PERCENT) / 100U;
    margins->warning_threshold = (total_capacity * RESOURCE_WARNING_THRESHOLD_PERCENT) / 100U;
    margins->critical_threshold = (total_capacity * RESOURCE_CRITICAL_THRESHOLD_PERCENT) / 100U;
    margins->emergency_threshold = (total_capacity * RESOURCE_EMERGENCY_THRESHOLD_PERCENT) / 100U;
    
    /* Initialize usage tracking */
    margins->current_usage = 0U;
    margins->margin_violation = false;
    
    return NASA_SUCCESS;
}
```

#### Resource Margin Validation
```c
/* NASA-compliant resource margin validation */
nasa_result_t nasa_validate_resource_margins(
    const nasa_resource_margins_t* margins
) {
    if (margins == NULL) {
        return NASA_ERROR_INVALID_PARAMETER;
    }
    
    /* Validate margin calculations */
    if (margins->warning_threshold >= margins->critical_threshold) {
        return NASA_ERROR_INVALID_RESOURCE_CONFIGURATION;
    }
    
    if (margins->critical_threshold >= margins->emergency_threshold) {
        return NASA_ERROR_INVALID_RESOURCE_CONFIGURATION;
    }
    
    if (margins->emergency_threshold >= margins->total_capacity) {
        return NASA_ERROR_INVALID_RESOURCE_CONFIGURATION;
    }
    
    /* Check current usage against thresholds */
    if (margins->current_usage > margins->emergency_threshold) {
        return NASA_ERROR_RESOURCE_EMERGENCY_THRESHOLD_EXCEEDED;
    }
    
    if (margins->current_usage > margins->critical_threshold) {
        return NASA_ERROR_RESOURCE_CRITICAL_THRESHOLD_EXCEEDED;
    }
    
    if (margins->current_usage > margins->warning_threshold) {
        return NASA_WARNING_RESOURCE_WARNING_THRESHOLD_EXCEEDED;
    }
    
    return NASA_SUCCESS;
}
```

### 2. Resource Oversubscription Management

#### Oversubscription Detection
```c
/* NASA-compliant oversubscription detection */
typedef enum {
    NASA_RESOURCE_STATUS_NORMAL = 0,
    NASA_RESOURCE_STATUS_WARNING,
    NASA_RESOURCE_STATUS_CRITICAL,
    NASA_RESOURCE_STATUS_EMERGENCY,
    NASA_RESOURCE_STATUS_OVERSUSCRIBED
} nasa_resource_status_t;

typedef struct {
    nasa_resource_margins_t margins;
    nasa_resource_status_t status;
    uint32_t oversubscription_count;
    uint32_t max_oversubscription_duration;
    bool graceful_degradation_enabled;
} nasa_resource_manager_t;

/* NASA-compliant oversubscription detection */
nasa_resource_status_t nasa_detect_resource_status(
    const nasa_resource_margins_t* margins
) {
    if (margins == NULL) {
        return NASA_RESOURCE_STATUS_EMERGENCY;
    }
    
    /* Check emergency threshold first */
    if (margins->current_usage > margins->emergency_threshold) {
        return NASA_RESOURCE_STATUS_EMERGENCY;
    }
    
    /* Check critical threshold */
    if (margins->current_usage > margins->critical_threshold) {
        return NASA_RESOURCE_STATUS_CRITICAL;
    }
    
    /* Check warning threshold */
    if (margins->current_usage > margins->warning_threshold) {
        return NASA_RESOURCE_STATUS_WARNING;
    }
    
    /* Check if safety margin is violated */
    if (margins->current_usage > (margins->total_capacity - margins->safety_margin)) {
        return NASA_RESOURCE_STATUS_WARNING;
    }
    
    return NASA_RESOURCE_STATUS_NORMAL;
}
```

#### Oversubscription Handling
```c
/* NASA-compliant oversubscription handling */
nasa_result_t nasa_handle_resource_oversubscription(
    nasa_resource_manager_t* manager,
    nasa_resource_status_t new_status
) {
    if (manager == NULL) {
        return NASA_ERROR_INVALID_PARAMETER;
    }
    
    nasa_result_t result = NASA_SUCCESS;
    
    switch (new_status) {
        case NASA_RESOURCE_STATUS_NORMAL:
            /* Normal operation - no action needed */
            break;
            
        case NASA_RESOURCE_STATUS_WARNING:
            /* Warning level - log and monitor */
            result = nasa_log_resource_warning(manager);
            break;
            
        case NASA_RESOURCE_STATUS_CRITICAL:
            /* Critical level - initiate recovery procedures */
            result = nasa_initiate_resource_recovery(manager);
            break;
            
        case NASA_RESOURCE_STATUS_EMERGENCY:
            /* Emergency level - activate safe mode */
            result = nasa_activate_resource_safe_mode(manager);
            break;
            
        case NASA_RESOURCE_STATUS_OVERSUSCRIBED:
            /* Oversubscribed - emergency shutdown procedures */
            result = nasa_emergency_resource_shutdown(manager);
            break;
            
        default:
            result = NASA_ERROR_INVALID_RESOURCE_STATUS;
            break;
    }
    
    if (result == NASA_SUCCESS) {
        manager->status = new_status;
    }
    
    return result;
}
```

#### Graceful Degradation
```c
/* NASA-compliant graceful degradation */
typedef struct {
    uint32_t priority_level;
    bool essential_function;
    nasa_result_t (*degradation_handler)(void* context);
    void* context;
} nasa_degradation_strategy_t;

/* NASA-compliant graceful degradation implementation */
nasa_result_t nasa_implement_graceful_degradation(
    nasa_resource_manager_t* manager,
    const nasa_degradation_strategy_t* strategies,
    uint32_t strategy_count
) {
    if (manager == NULL || strategies == NULL) {
        return NASA_ERROR_INVALID_PARAMETER;
    }
    
    if (!manager->graceful_degradation_enabled) {
        return NASA_ERROR_GRACEFUL_DEGRADATION_DISABLED;
    }
    
    nasa_result_t result = NASA_SUCCESS;
    
    /* Sort strategies by priority (highest first) */
    nasa_degradation_strategy_t sorted_strategies[NASA_MAX_DEGRADATION_STRATEGIES];
    result = nasa_sort_degradation_strategies(strategies, strategy_count, sorted_strategies);
    if (result != NASA_SUCCESS) {
        return result;
    }
    
    /* Apply degradation strategies in priority order */
    for (uint32_t i = 0U; i < strategy_count; i++) {
        if (sorted_strategies[i].degradation_handler != NULL) {
            result = sorted_strategies[i].degradation_handler(sorted_strategies[i].context);
            if (result != NASA_SUCCESS) {
                /* Log degradation failure but continue with other strategies */
                nasa_log_degradation_failure(&sorted_strategies[i], result);
            }
        }
    }
    
    return NASA_SUCCESS;
}
```

### 3. Resource Usage Measurement

#### Comprehensive Resource Monitoring
```c
/* NASA-compliant resource usage measurement */
typedef struct {
    uint32_t cpu_usage_percent;
    uint32_t memory_usage_bytes;
    uint32_t stack_usage_bytes;
    uint32_t heap_usage_bytes;
    uint32_t file_descriptor_count;
    uint32_t network_connection_count;
    uint32_t thread_count;
    uint64_t timestamp;
} nasa_resource_usage_t;

typedef struct {
    nasa_resource_usage_t current;
    nasa_resource_usage_t peak;
    nasa_resource_usage_t average;
    uint32_t measurement_count;
    uint64_t last_measurement_time;
} nasa_resource_monitor_t;

/* NASA-compliant resource usage measurement */
nasa_result_t nasa_measure_resource_usage(
    nasa_resource_monitor_t* monitor
) {
    if (monitor == NULL) {
        return NASA_ERROR_INVALID_PARAMETER;
    }
    
    nasa_resource_usage_t current_usage;
    nasa_result_t result = NASA_SUCCESS;
    
    /* Measure CPU usage */
    result = nasa_measure_cpu_usage(&current_usage.cpu_usage_percent);
    if (result != NASA_SUCCESS) {
        return result;
    }
    
    /* Measure memory usage */
    result = nasa_measure_memory_usage(&current_usage.memory_usage_bytes);
    if (result != NASA_SUCCESS) {
        return result;
    }
    
    /* Measure stack usage */
    result = nasa_measure_stack_usage(&current_usage.stack_usage_bytes);
    if (result != NASA_SUCCESS) {
        return result;
    }
    
    /* Measure heap usage (if applicable) */
    result = nasa_measure_heap_usage(&current_usage.heap_usage_bytes);
    if (result != NASA_SUCCESS) {
        return result;
    }
    
    /* Measure system resources */
    result = nasa_measure_system_resources(&current_usage);
    if (result != NASA_SUCCESS) {
        return result;
    }
    
    /* Update timestamp */
    current_usage.timestamp = nasa_get_system_timestamp();
    
    /* Update monitor with current measurements */
    result = nasa_update_resource_monitor(monitor, &current_usage);
    
    return result;
}
```

#### Resource Usage Trend Analysis
```c
/* NASA-compliant resource usage trend analysis */
typedef struct {
    float growth_rate;
    float peak_trend;
    float average_trend;
    bool increasing_trend;
    bool decreasing_trend;
    bool stable_trend;
    uint32_t prediction_horizon;
} nasa_resource_trend_t;

/* NASA-compliant trend analysis */
nasa_result_t nasa_analyze_resource_trends(
    const nasa_resource_monitor_t* monitor,
    nasa_resource_trend_t* trends
) {
    if (monitor == NULL || trends == NULL) {
        return NASA_ERROR_INVALID_PARAMETER;
    }
    
    if (monitor->measurement_count < 2U) {
        return NASA_ERROR_INSUFFICIENT_DATA_FOR_TREND_ANALYSIS;
    }
    
    nasa_result_t result = NASA_SUCCESS;
    
    /* Calculate growth rate */
    result = nasa_calculate_growth_rate(monitor, &trends->growth_rate);
    if (result != NASA_SUCCESS) {
        return result;
    }
    
    /* Calculate peak trend */
    result = nasa_calculate_peak_trend(monitor, &trends->peak_trend);
    if (result != NASA_SUCCESS) {
        return result;
    }
    
    /* Calculate average trend */
    result = nasa_calculate_average_trend(monitor, &trends->average_trend);
    if (result != NASA_SUCCESS) {
        return result;
    }
    
    /* Determine trend direction */
    if (trends->growth_rate > NASA_TREND_THRESHOLD_POSITIVE) {
        trends->increasing_trend = true;
        trends->decreasing_trend = false;
        trends->stable_trend = false;
    } else if (trends->growth_rate < NASA_TREND_THRESHOLD_NEGATIVE) {
        trends->increasing_trend = false;
        trends->decreasing_trend = true;
        trends->stable_trend = false;
    } else {
        trends->increasing_trend = false;
        trends->decreasing_trend = false;
        trends->stable_trend = true;
    }
    
    /* Set prediction horizon */
    trends->prediction_horizon = NASA_DEFAULT_PREDICTION_HORIZON;
    
    return NASA_SUCCESS;
}
```

### 4. Resource Allocation

#### Safe Resource Allocation
```c
/* NASA-compliant resource allocation */
typedef struct {
    uint32_t resource_id;
    uint32_t requested_amount;
    uint32_t allocated_amount;
    uint32_t safety_margin;
    bool allocation_successful;
    nasa_result_t allocation_result;
} nasa_resource_allocation_t;

/* NASA-compliant resource allocation with margin checking */
nasa_result_t nasa_allocate_resource_with_margins(
    nasa_resource_manager_t* manager,
    uint32_t requested_amount,
    nasa_resource_allocation_t* allocation
) {
    if (manager == NULL || allocation == NULL) {
        return NASA_ERROR_INVALID_PARAMETER;
    }
    
    if (requested_amount == 0U) {
        return NASA_ERROR_INVALID_RESOURCE_REQUEST;
    }
    
    nasa_result_t result = NASA_SUCCESS;
    
    /* Check if allocation would violate safety margins */
    uint32_t total_required = requested_amount + manager->margins.safety_margin;
    if ((manager->margins.current_usage + total_required) > 
        (manager->margins.total_capacity - manager->margins.safety_margin)) {
        
        allocation->allocation_successful = false;
        allocation->allocation_result = NASA_ERROR_RESOURCE_SAFETY_MARGIN_VIOLATION;
        return NASA_ERROR_RESOURCE_SAFETY_MARGIN_VIOLATION;
    }
    
    /* Check if allocation would exceed critical threshold */
    if ((manager->margins.current_usage + requested_amount) > 
        manager->margins.critical_threshold) {
        
        allocation->allocation_successful = false;
        allocation->allocation_result = NASA_ERROR_RESOURCE_CRITICAL_THRESHOLD_EXCEEDED;
        return NASA_ERROR_RESOURCE_CRITICAL_THRESHOLD_EXCEEDED;
    }
    
    /* Perform actual resource allocation */
    result = nasa_perform_resource_allocation(requested_amount, &allocation->allocated_amount);
    if (result != NASA_SUCCESS) {
        allocation->allocation_successful = false;
        allocation->allocation_result = result;
        return result;
    }
    
    /* Update resource manager */
    manager->margins.current_usage += allocation->allocated_amount;
    
    /* Set allocation details */
    allocation->resource_id = nasa_generate_resource_id();
    allocation->requested_amount = requested_amount;
    allocation->safety_margin = manager->margins.safety_margin;
    allocation->allocation_successful = true;
    allocation->allocation_result = NASA_SUCCESS;
    
    return NASA_SUCCESS;
}
```

#### Resource Deallocation
```c
/* NASA-compliant resource deallocation */
nasa_result_t nasa_deallocate_resource(
    nasa_resource_manager_t* manager,
    const nasa_resource_allocation_t* allocation
) {
    if (manager == NULL || allocation == NULL) {
        return NASA_ERROR_INVALID_PARAMETER;
    }
    
    if (!allocation->allocation_successful) {
        return NASA_ERROR_INVALID_ALLOCATION;
    }
    
    nasa_result_t result = NASA_SUCCESS;
    
    /* Perform actual resource deallocation */
    result = nasa_perform_resource_deallocation(allocation->allocated_amount);
    if (result != NASA_SUCCESS) {
        return result;
    }
    
    /* Update resource manager */
    if (manager->margins.current_usage >= allocation->allocated_amount) {
        manager->margins.current_usage -= allocation->allocated_amount;
    } else {
        /* Handle underflow - this should never happen in NASA systems */
        manager->margins.current_usage = 0U;
        nasa_log_resource_underflow(allocation->allocated_amount);
    }
    
    return NASA_SUCCESS;
}
```

## Implementation Guidelines

### 1. Resource Margin Configuration
- **Safety Margin**: Always maintain at least 20% safety margin
- **Warning Threshold**: Set at 70% of total capacity
- **Critical Threshold**: Set at 85% of total capacity
- **Emergency Threshold**: Set at 95% of total capacity

### 2. Oversubscription Prevention
- **Pre-allocation Checks**: Validate resource availability before allocation
- **Margin Validation**: Ensure safety margins are never violated
- **Threshold Monitoring**: Continuous monitoring of all threshold levels
- **Graceful Degradation**: Implement degradation strategies for critical situations

### 3. Resource Monitoring
- **Continuous Measurement**: Real-time resource usage monitoring
- **Trend Analysis**: Analyze usage patterns and predict future needs
- **Peak Tracking**: Track peak usage for capacity planning
- **Historical Data**: Maintain usage history for analysis

### 4. Allocation Safety
- **Atomic Operations**: Ensure allocation/deallocation operations are atomic
- **Margin Checking**: Always check safety margins before allocation
- **Threshold Validation**: Validate against all threshold levels
- **Rollback Capability**: Ability to rollback failed allocations

## Compliance Requirements

### NASA Power of 10 Compliance
- **Rule 1**: No dynamic memory allocation after initialization
- **Rule 2**: No recursion or unbounded loops
- **Rule 3**: No complex data structures
- **Rule 4**: No floating-point operations
- **Rule 5**: No dynamic loading of code

### MISRA C Compliance
- **Rule 4.1**: No use of octal constants
- **Rule 5.1**: No use of identifiers with external linkage
- **Rule 7.1**: No use of octal escape sequences
- **Rule 8.1**: No use of functions with variable argument lists

### JPL Standards Compliance
- **Rule 6**: Resource usage must be bounded and predictable
- **Rule 7**: Resource allocation must be deterministic
- **Rule 9**: Resource monitoring must be continuous
- **Rule 10**: Resource recovery must be graceful

## Testing and Validation

### 1. Resource Margin Testing
- **Safety Margin Validation**: Verify safety margins are never violated
- **Threshold Testing**: Test all threshold levels and responses
- **Boundary Testing**: Test edge cases and boundary conditions
- **Stress Testing**: Test under maximum resource utilization

### 2. Oversubscription Testing
- **Oversubscription Detection**: Verify detection mechanisms work correctly
- **Recovery Procedures**: Test recovery and degradation strategies
- **Graceful Degradation**: Validate degradation implementation
- **Emergency Procedures**: Test emergency shutdown procedures

### 3. Resource Monitoring Testing
- **Measurement Accuracy**: Verify measurement accuracy and precision
- **Trend Analysis**: Test trend analysis algorithms
- **Performance Impact**: Measure monitoring overhead
- **Data Integrity**: Validate monitoring data integrity

### 4. Allocation Testing
- **Allocation Safety**: Verify allocation safety mechanisms
- **Margin Compliance**: Test margin checking and validation
- **Threshold Enforcement**: Validate threshold enforcement
- **Rollback Testing**: Test allocation rollback capabilities

## Conclusion

This document provides comprehensive coverage of NASA-compliant resource management and oversubscription handling. It ensures robust resource utilization, safety margins, and graceful degradation under resource constraints, meeting all NASA safety-critical system requirements.

**Key Takeaways:**
1. **Always maintain safety margins** - Never allocate resources that would violate safety margins
2. **Implement comprehensive monitoring** - Continuous monitoring of all resource usage
3. **Plan for oversubscription** - Implement graceful degradation and recovery strategies
4. **Validate all allocations** - Check margins and thresholds before any resource allocation
5. **Test thoroughly** - Comprehensive testing of all resource management scenarios

Users can now train their ML models with **100% confidence** that they will detect violations across all resource management and oversubscription patterns required for NASA compliance.
