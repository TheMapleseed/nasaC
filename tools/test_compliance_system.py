#!/usr/bin/env python3
"""
Test Script for NASA C Code Compliance System

This script tests the compliance checker and evaluator to ensure
they work correctly with various code samples.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from tools.compliance_checker import NASAComplianceChecker

def test_compliant_code():
    """Test with compliant code."""
    print("Testing compliant code...")
    
    compliant_code = """
#include <stdint.h>

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
}
"""
    
    checker = NASAComplianceChecker()
    checker.load_code(compliant_code)
    violations = checker.check_all_rules()
    
    print(f"Compliance Score: {checker.calculate_compliance_score()}")
    print(f"Compliance Level: {checker.get_compliance_level()}")
    print(f"Violations Found: {len(violations)}")
    
    if violations:
        print("Unexpected violations found!")
        for violation in violations:
            print(f"  - {violation.rule_name}: {violation.description}")
        return False
    else:
        print("✓ Compliant code correctly identified")
        return True

def test_non_compliant_code():
    """Test with non-compliant code."""
    print("\nTesting non-compliant code...")
    
    non_compliant_code = """
#include <stdio.h>
#include <stdlib.h>

int process_data(int x, int y, int z, int w, int v) {
    int temp;
    int result;
    
    if (x < 0) return -1;
    if (x > 100) return -2;
    
    temp = malloc(100);
    if (temp == NULL) return -3;
    
    while (y > 0) {
        result = x + y + z + w + v;
        y--;
    }
    
    free(temp);
    return result;
}

int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

void cleanup() {
    goto cleanup_label;
    
cleanup_label:
    printf("Cleanup complete\\n");
}

int main() {
    int a, b, c;
    
    a = b = c = 0;
    
    while ((a = getchar()) != EOF) {
        if (process_data(a, b, c, 1, 2) > 0) {
            break;
        }
    }
    
    return 0;
}
"""
    
    checker = NASAComplianceChecker()
    checker.load_code(non_compliant_code)
    violations = checker.check_all_rules()
    
    print(f"Compliance Score: {checker.calculate_compliance_score()}")
    print(f"Compliance Level: {checker.get_compliance_level()}")
    print(f"Violations Found: {len(violations)}")
    
    if violations:
        print("✓ Violations correctly identified:")
        for violation in violations:
            print(f"  - {violation.rule_name} (Severity: {violation.severity.value})")
            print(f"    Description: {violation.description}")
        return True
    else:
        print("✗ No violations found in non-compliant code!")
        return False

def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("\nTesting edge cases...")
    
    # Test empty code
    print("Testing empty code...")
    checker = NASAComplianceChecker()
    checker.load_code("")
    violations = checker.check_all_rules()
    print(f"Empty code violations: {len(violations)}")
    
    # Test single line
    print("Testing single line...")
    checker.load_code("int main() { return 0; }")
    violations = checker.check_all_rules()
    print(f"Single line violations: {len(violations)}")
    
    # Test code with only comments
    print("Testing comment-only code...")
    comment_code = """
// This is a comment
/* Another comment */
// More comments
"""
    checker.load_code(comment_code)
    violations = checker.check_all_rules()
    print(f"Comment-only code violations: {len(violations)}")
    
    return True

def test_rule_specific_violations():
    """Test specific rule violations."""
    print("\nTesting specific rule violations...")
    
    # Test goto violation
    goto_code = """
int main() {
    int x = 5;
    if (x < 0) goto error;
    return x;
error:
    return -1;
}
"""
    checker = NASAComplianceChecker()
    checker.load_code(goto_code)
    violations = checker.check_all_rules()
    
    goto_violations = [v for v in violations if 'goto' in v.description.lower()]
    if goto_violations:
        print("✓ Goto violation correctly detected")
    else:
        print("✗ Goto violation not detected")
    
    # Test malloc violation
    malloc_code = """
int main() {
    int* ptr = malloc(100);
    free(ptr);
    return 0;
}
"""
    checker.load_code(malloc_code)
    violations = checker.check_all_rules()
    
    malloc_violations = [v for v in violations if 'malloc' in v.description.lower()]
    if malloc_violations:
        print("✓ Malloc violation correctly detected")
    else:
        print("✗ Malloc violation not detected")
    
    return True

def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("NASA C Code Compliance System Tests")
    print("=" * 50)
    
    tests = [
        ("Compliant Code Test", test_compliant_code),
        ("Non-Compliant Code Test", test_non_compliant_code),
        ("Edge Cases Test", test_edge_cases),
        ("Rule-Specific Violations Test", test_rule_specific_violations)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The compliance system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
