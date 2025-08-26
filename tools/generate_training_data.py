#!/usr/bin/env python3
"""
Training Data Generator for NASA C Code Compliance

This script helps generate additional training examples by creating
variations of existing code samples and synthetic examples.
"""

import json
import random
import re
from pathlib import Path
from typing import Dict, List, Any
import argparse

class TrainingDataGenerator:
    """Generates training data for NASA C compliance ML training."""
    
    def __init__(self):
        self.violation_patterns = {
            'rule_1': {
                'goto': 'goto cleanup;',
                'recursion': 'return n * factorial(n - 1);',
                'setjmp': 'setjmp(env);'
            },
            'rule_2': {
                'unbounded_while': 'while (condition) {',
                'infinite_loop': 'while (1) {'
            },
            'rule_3': {
                'malloc': 'int* ptr = malloc(size);',
                'free': 'free(ptr);'
            },
            'rule_4': {
                'many_params': 'int func(int a, int b, int c, int d, int e) {'
            },
            'rule_5': {
                'triple_pointer': 'int value = ***ptr;'
            },
            'rule_6': {
                'mid_declaration': 'int x = 5;\n    // ... code ...\n    int y = 10;'
            },
            'rule_7': {
                'multiple_returns': 'if (x < 0) return -1;\n    if (x > 100) return -2;\n    return 0;'
            },
            'rule_8': {
                'define': '#define MAX_SIZE 100',
                'macro': '#define SQUARE(x) ((x) * (x))'
            },
            'rule_9': {
                'assignment_in_condition': 'while ((ch = getchar()) != EOF) {'
            },
            'rule_10': {
                'multiple_assignments': 'a = b = c = 0;'
            }
        }
    
    def generate_compliant_example(self, complexity: str = 'intermediate') -> Dict[str, Any]:
        """Generate a compliant code example."""
        if complexity == 'beginner':
            code = self._generate_beginner_compliant()
        elif complexity == 'intermediate':
            code = self._generate_intermediate_compliant()
        else:
            code = self._generate_advanced_compliant()
        
        return {
            "code_sample": code,
            "compliance_score": random.randint(95, 100),
            "compliance_level": "fully_compliant",
            "violations": [],
            "annotations": self._analyze_code(code),
            "tags": self._generate_tags(complexity),
            "difficulty": complexity
        }
    
    def generate_non_compliant_example(self, complexity: str = 'intermediate', 
                                     violation_count: int = 3) -> Dict[str, Any]:
        """Generate a non-compliant code example."""
        violations = []
        code = self._generate_base_code(complexity)
        
        # Add violations
        available_rules = list(self.violation_patterns.keys())
        selected_rules = random.sample(available_rules, min(violation_count, len(available_rules)))
        
        for rule in selected_rules:
            violation = self._create_violation(rule, code)
            if violation:
                violations.append(violation)
                code = self._inject_violation(code, rule)
        
        # Calculate compliance score
        compliance_score = max(0, 100 - len(violations) * 15)
        
        return {
            "code_sample": code,
            "compliance_score": compliance_score,
            "compliance_level": self._get_compliance_level(compliance_score),
            "violations": violations,
            "annotations": self._analyze_code(code),
            "tags": self._generate_tags(complexity, violations),
            "difficulty": complexity
        }
    
    def _generate_beginner_compliant(self) -> str:
        """Generate beginner-level compliant code."""
        return '''#include <stdint.h>

int main(void) {
    uint16_t counter;
    uint16_t result;
    
    counter = 0;
    result = 0;
    
    while (counter < 10) {
        result += counter;
        counter++;
    }
    
    return (int)result;
}'''
    
    def _generate_intermediate_compliant(self) -> str:
        """Generate intermediate-level compliant code."""
        return '''#include <stdint.h>
#include <stdbool.h>

#define MAX_ARRAY_SIZE 100

typedef struct {
    uint16_t values[MAX_ARRAY_SIZE];
    uint8_t count;
} data_array_t;

bool add_value(data_array_t* array, uint16_t value) {
    bool success = false;
    
    if (array != NULL && array->count < MAX_ARRAY_SIZE) {
        array->values[array->count] = value;
        array->count++;
        success = true;
    }
    
    return success;
}

uint16_t calculate_sum(const data_array_t* array) {
    uint16_t sum = 0;
    uint8_t index = 0;
    
    if (array == NULL) {
        return sum;
    }
    
    while (index < array->count && index < MAX_ARRAY_SIZE) {
        sum += array->values[index];
        index++;
    }
    
    return sum;
}

int main(void) {
    data_array_t data;
    uint16_t total;
    
    data.count = 0;
    add_value(&data, 10);
    add_value(&data, 20);
    add_value(&data, 30);
    
    total = calculate_sum(&data);
    
    return (int)total;
}'''
    
    def _generate_advanced_compliant(self) -> str:
        """Generate advanced-level compliant code."""
        return '''#include <stdint.h>
#include <stdbool.h>

#define MAX_SENSORS 16
#define MAX_READINGS 1000
#define TEMP_THRESHOLD 150

typedef struct {
    uint16_t sensor_id;
    int16_t temperature;
    bool is_active;
    uint32_t reading_count;
} sensor_t;

typedef struct {
    sensor_t sensors[MAX_SENSORS];
    uint8_t active_count;
    uint32_t total_readings;
} sensor_system_t;

typedef struct {
    uint16_t sensor_id;
    int16_t temperature;
    uint32_t timestamp;
} reading_t;

bool initialize_sensor_system(sensor_system_t* system) {
    bool success = false;
    uint8_t index = 0;
    
    if (system != NULL) {
        system->active_count = 0;
        system->total_readings = 0;
        
        while (index < MAX_SENSORS) {
            system->sensors[index].sensor_id = index;
            system->sensors[index].is_active = false;
            system->sensors[index].reading_count = 0;
            index++;
        }
        
        success = true;
    }
    
    return success;
}

bool add_sensor_reading(sensor_system_t* system, reading_t reading) {
    bool success = false;
    uint8_t index = 0;
    
    if (system != NULL && reading.sensor_id < MAX_SENSORS) {
        while (index < MAX_SENSORS) {
            if (system->sensors[index].sensor_id == reading.sensor_id) {
                if (reading.temperature < TEMP_THRESHOLD) {
                    system->sensors[index].temperature = reading.temperature;
                    system->sensors[index].reading_count++;
                    system->total_readings++;
                    success = true;
                }
                break;
            }
            index++;
        }
    }
    
    return success;
}

uint32_t get_system_statistics(const sensor_system_t* system) {
    uint32_t total_readings = 0;
    uint8_t index = 0;
    
    if (system != NULL) {
        while (index < MAX_SENSORS) {
            total_readings += system->sensors[index].reading_count;
            index++;
        }
    }
    
    return total_readings;
}

int main(void) {
    sensor_system_t system;
    reading_t reading;
    bool init_success;
    uint32_t stats;
    
    init_success = initialize_sensor_system(&system);
    
    if (init_success) {
        reading.sensor_id = 0;
        reading.temperature = 25;
        reading.timestamp = 1000;
        
        add_sensor_reading(&system, reading);
        stats = get_system_statistics(&system);
    }
    
    return (int)stats;
}'''
    
    def _generate_base_code(self, complexity: str) -> str:
        """Generate base code for non-compliant examples."""
        if complexity == 'beginner':
            return '''#include <stdio.h>

int main() {
    int x, y, z;
    
    x = 5;
    y = 10;
    z = x + y;
    
    return z;
}'''
        elif complexity == 'intermediate':
            return '''#include <stdio.h>
#include <stdlib.h>

int process_data(int a, int b) {
    int result;
    
    result = a + b;
    
    return result;
}

int main() {
    int result;
    
    result = process_data(5, 10);
    
    return result;
}'''
        else:
            return '''#include <stdio.h>
#include <stdlib.h>

int calculate_value(int x, int y, int z) {
    int temp;
    int result;
    
    temp = x + y;
    result = temp * z;
    
    return result;
}

int main() {
    int value;
    
    value = calculate_value(1, 2, 3);
    
    return value;
}'''
    
    def _create_violation(self, rule: str, code: str) -> Dict[str, Any]:
        """Create a violation object for a specific rule."""
        rule_names = {
            'rule_1': 'Avoid Complex Flow Control',
            'rule_2': 'Fixed Loop Bounds',
            'rule_3': 'No Dynamic Memory',
            'rule_4': 'Function Parameters',
            'rule_5': 'Pointer Dereferencing',
            'rule_6': 'Variable Declarations',
            'rule_7': 'Single Return Point',
            'rule_8': 'Preprocessor Usage',
            'rule_9': 'Assignment in Expressions',
            'rule_10': 'Multiple Assignments'
        }
        
        severity_levels = {
            'rule_1': 'critical',
            'rule_2': 'major',
            'rule_3': 'critical',
            'rule_4': 'major',
            'rule_5': 'major',
            'rule_6': 'minor',
            'rule_7': 'moderate',
            'rule_8': 'minor',
            'rule_9': 'moderate',
            'rule_10': 'minor'
        }
        
        return {
            "rule_id": rule,
            "rule_name": rule_names.get(rule, "Unknown Rule"),
            "description": f"Violation of {rule_names.get(rule, 'Unknown Rule')}",
            "severity": severity_levels.get(rule, "minor"),
            "line_number": random.randint(1, 20),
            "suggestion": f"Fix {rule_names.get(rule, 'Unknown Rule')} violation"
        }
    
    def _inject_violation(self, code: str, rule: str) -> str:
        """Inject a violation into the code."""
        if rule == 'rule_1' and 'goto' in self.violation_patterns[rule]:
            # Add goto statement
            lines = code.split('\n')
            if len(lines) > 3:
                lines.insert(-2, '    goto cleanup;')
                lines.insert(-1, 'cleanup:')
                return '\n'.join(lines)
        
        elif rule == 'rule_3' and 'malloc' in self.violation_patterns[rule]:
            # Add malloc
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if 'int main' in line:
                    lines.insert(i + 1, '    int* ptr = malloc(100);')
                    lines.insert(i + 2, '    free(ptr);')
                    break
            return '\n'.join(lines)
        
        elif rule == 'rule_4':
            # Add more parameters
            code = code.replace('int process_data(int a, int b)', 
                              'int process_data(int a, int b, int c, int d, int e)')
        
        elif rule == 'rule_8':
            # Add #define
            lines = code.split('\n')
            lines.insert(1, '#define MAX_SIZE 100')
            return '\n'.join(lines)
        
        elif rule == 'rule_10':
            # Add multiple assignments
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if 'int x, y, z;' in line:
                    lines.insert(i + 1, '    x = y = z = 0;')
                    break
            return '\n'.join(lines)
        
        return code
    
    def _analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code and extract features."""
        lines = code.split('\n')
        
        return {
            "function_count": len(re.findall(r'\w+\s+\w+\s*\([^)]*\)\s*\{?', code)),
            "line_count": len(lines),
            "complexity_score": self._calculate_complexity(code),
            "nesting_depth": self._calculate_nesting_depth(code),
            "variable_count": len(re.findall(r'\b(int|char|float|double|long|short|unsigned|signed)\s+\w+', code)),
            "pointer_count": len(re.findall(r'\*+\w+|\w+\s*\*+\s*\w+', code)),
            "loop_count": len(re.findall(r'\b(for|while|do)\b', code)),
            "conditional_count": len(re.findall(r'\b(if|else|switch|case)\b', code))
        }
    
    def _calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        decision_keywords = ['if', 'else', 'while', 'for', 'case', 'catch', '&&', '||']
        for keyword in decision_keywords:
            complexity += code.count(keyword)
        return complexity
    
    def _calculate_nesting_depth(self, code: str) -> int:
        """Calculate maximum nesting depth."""
        max_depth = 0
        current_depth = 0
        
        for char in code:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth -= 1
        
        return max_depth
    
    def _generate_tags(self, complexity: str, violations: List[Dict] = None) -> List[str]:
        """Generate tags for the code sample."""
        tags = [complexity, "synthetic"]
        
        if violations:
            for violation in violations:
                tags.append(violation['rule_id'])
        
        return tags
    
    def _get_compliance_level(self, score: int) -> str:
        """Get compliance level based on score."""
        if score >= 90:
            return "fully_compliant"
        elif score >= 80:
            return "minor_issues"
        elif score >= 70:
            return "moderate_issues"
        elif score >= 60:
            return "major_issues"
        else:
            return "non_compliant"
    
    def generate_dataset(self, output_dir: str, num_examples: int = 50):
        """Generate a complete training dataset."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        compliant_dir = output_path / 'compliant_examples'
        non_compliant_dir = output_path / 'non_compliant_examples'
        
        compliant_dir.mkdir(exist_ok=True)
        non_compliant_dir.mkdir(exist_ok=True)
        
        # Generate compliant examples
        for i in range(num_examples // 2):
            complexity = random.choice(['beginner', 'intermediate', 'advanced'])
            example = self.generate_compliant_example(complexity)
            
            filename = f"generated_compliant_{i+1:03d}.json"
            with open(compliant_dir / filename, 'w') as f:
                json.dump(example, f, indent=2)
        
        # Generate non-compliant examples
        for i in range(num_examples // 2):
            complexity = random.choice(['beginner', 'intermediate', 'advanced'])
            violation_count = random.randint(2, 6)
            example = self.generate_non_compliant_example(complexity, violation_count)
            
            filename = f"generated_non_compliant_{i+1:03d}.json"
            with open(non_compliant_dir / filename, 'w') as f:
                json.dump(example, f, indent=2)
        
        print(f"Generated {num_examples} training examples in {output_dir}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Generate training data for NASA C compliance')
    parser.add_argument('--output-dir', default='../training_data', help='Output directory for generated data')
    parser.add_argument('--num-examples', type=int, default=50, help='Number of examples to generate')
    parser.add_argument('--compliant-only', action='store_true', help='Generate only compliant examples')
    parser.add_argument('--non-compliant-only', action='store_true', help='Generate only non-compliant examples')
    
    args = parser.parse_args()
    
    generator = TrainingDataGenerator()
    
    if args.compliant_only:
        # Generate only compliant examples
        for i in range(args.num_examples):
            complexity = random.choice(['beginner', 'intermediate', 'advanced'])
            example = generator.generate_compliant_example(complexity)
            
            output_path = Path(args.output_dir) / 'compliant_examples'
            output_path.mkdir(exist_ok=True)
            
            filename = f"generated_compliant_{i+1:03d}.json"
            with open(output_path / filename, 'w') as f:
                json.dump(example, f, indent=2)
        
        print(f"Generated {args.num_examples} compliant examples")
    
    elif args.non_compliant_only:
        # Generate only non-compliant examples
        for i in range(args.num_examples):
            complexity = random.choice(['beginner', 'intermediate', 'advanced'])
            violation_count = random.randint(2, 6)
            example = generator.generate_non_compliant_example(complexity, violation_count)
            
            output_path = Path(args.output_dir) / 'non_compliant_examples'
            output_path.mkdir(exist_ok=True)
            
            filename = f"generated_non_compliant_{i+1:03d}.json"
            with open(output_path / filename, 'w') as f:
                json.dump(example, f, indent=2)
        
        print(f"Generated {args.num_examples} non-compliant examples")
    
    else:
        # Generate balanced dataset
        generator.generate_dataset(args.output_dir, args.num_examples)

if __name__ == '__main__':
    main()
