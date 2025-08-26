#!/usr/bin/env python3
"""
NASA C Code Compliance Checker

A standalone tool for checking C code compliance with NASA standards
without requiring trained machine learning models.
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json

class Severity(Enum):
    """Violation severity levels."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"

@dataclass
class Violation:
    """Represents a coding standard violation."""
    rule_id: str
    rule_name: str
    description: str
    severity: Severity
    line_number: int
    suggestion: str
    code_snippet: str = ""

class NASAComplianceChecker:
    """Checks C code for compliance with NASA standards."""
    
    def __init__(self):
        self.violations = []
        self.code_lines = []
        
    def load_code(self, code: str):
        """Load code for analysis."""
        self.code_lines = code.split('\n')
        self.violations = []
    
    def check_all_rules(self) -> List[Violation]:
        """Check all NASA coding standards."""
        self.violations = []
        
        # Check Power of 10 rules
        self._check_rule_1_flow_control()
        self._check_rule_2_loop_bounds()
        self._check_rule_3_dynamic_memory()
        self._check_rule_4_function_parameters()
        self._check_rule_5_pointer_dereferencing()
        self._check_rule_6_variable_declarations()
        self._check_rule_7_single_return()
        self._check_rule_8_preprocessor()
        self._check_rule_9_assignment_expressions()
        self._check_rule_10_multiple_assignments()
        
        # Check additional style rules
        self._check_naming_conventions()
        self._check_function_length()
        self._check_comment_coverage()
        self._check_error_handling()
        self._check_type_safety()
        
        return self.violations
    
    def _check_rule_1_flow_control(self):
        """Rule 1: Avoid Complex Flow Control."""
        for i, line in enumerate(self.code_lines, 1):
            # Check for goto
            if 'goto' in line and not line.strip().startswith('//'):
                self.violations.append(Violation(
                    rule_id="rule_1",
                    rule_name="Avoid Complex Flow Control",
                    description="Use of goto statement detected",
                    severity=Severity.CRITICAL,
                    line_number=i,
                    suggestion="Replace goto with structured control flow",
                    code_snippet=line.strip()
                ))
            
            # Check for setjmp/longjmp
            if ('setjmp' in line or 'longjmp' in line) and not line.strip().startswith('//'):
                self.violations.append(Violation(
                    rule_id="rule_1",
                    rule_name="Avoid Complex Flow Control",
                    description="Use of setjmp/longjmp detected",
                    severity=Severity.CRITICAL,
                    line_number=i,
                    suggestion="Use structured error handling instead",
                    code_snippet=line.strip()
                ))
            
            # Check for recursion (simplified check)
            if re.search(r'\w+\s*\([^)]*\)\s*\{', line):
                # Look for function calls in the same function
                func_name = re.search(r'(\w+)\s*\([^)]*\)\s*\{', line)
                if func_name:
                    func_name = func_name.group(1)
                    # Check if function calls itself (basic recursion detection)
                    for j, check_line in enumerate(self.code_lines[i:], i+1):
                        if f'{func_name}(' in check_line and not check_line.strip().startswith('//'):
                            self.violations.append(Violation(
                                rule_id="rule_1",
                                rule_name="Avoid Complex Flow Control",
                                description="Recursive function call detected",
                                severity=Severity.CRITICAL,
                                line_number=i,
                                suggestion="Use iterative approach instead of recursion",
                                code_snippet=line.strip()
                            ))
                            break
    
    def _check_rule_2_loop_bounds(self):
        """Rule 2: All Loops Must Have Fixed Upper Bounds."""
        for i, line in enumerate(self.code_lines, 1):
            # Check while loops
            if re.match(r'\s*while\s*\(', line):
                # Look for bounded patterns
                if not any(pattern in line for pattern in ['MAX_', 'count', 'size', 'length']):
                    self.violations.append(Violation(
                        rule_id="rule_2",
                        rule_name="Fixed Loop Bounds",
                        description="Loop without clear upper bound detected",
                        severity=Severity.MAJOR,
                        line_number=i,
                        suggestion="Add compile-time determinable upper bound",
                        code_snippet=line.strip()
                    ))
            
            # Check for loops with potential infinite conditions
            if 'while' in line and any(pattern in line for pattern in ['true', '1', '!0']):
                self.violations.append(Violation(
                    rule_id="rule_2",
                    rule_name="Fixed Loop Bounds",
                    description="Potential infinite loop detected",
                    severity=Severity.MAJOR,
                    line_number=i,
                    suggestion="Add explicit loop counter and bounds checking",
                    code_snippet=line.strip()
                ))
    
    def _check_rule_3_dynamic_memory(self):
        """Rule 3: Avoid Dynamic Memory Allocation."""
        for i, line in enumerate(self.code_lines, 1):
            if any(func in line for func in ['malloc', 'calloc', 'realloc', 'free']):
                if not line.strip().startswith('//'):
                    self.violations.append(Violation(
                        rule_id="rule_3",
                        rule_name="No Dynamic Memory",
                        description="Dynamic memory allocation detected",
                        severity=Severity.CRITICAL,
                        line_number=i,
                        suggestion="Use static allocation or stack-based allocation",
                        code_snippet=line.strip()
                    ))
    
    def _check_rule_4_function_parameters(self):
        """Rule 4: No Function Calls with More Than 2 Arguments."""
        for i, line in enumerate(self.code_lines, 1):
            # Check function definitions
            func_match = re.search(r'\w+\s+\w+\s*\(([^)]*)\)\s*\{?', line)
            if func_match:
                params = func_match.group(1)
                param_count = len([p.strip() for p in params.split(',') if p.strip()])
                if param_count > 2:
                    self.violations.append(Violation(
                        rule_id="rule_4",
                        rule_name="Function Parameters",
                        description=f"Function with {param_count} parameters detected",
                        severity=Severity.MAJOR,
                        line_number=i,
                        suggestion="Use structure to group related parameters",
                        code_snippet=line.strip()
                    ))
    
    def _check_rule_5_pointer_dereferencing(self):
        """Rule 5: Avoid Pointer Dereferencing More Than 2 Levels."""
        for i, line in enumerate(self.code_lines, 1):
            if '***' in line:
                self.violations.append(Violation(
                    rule_id="rule_5",
                    rule_name="Pointer Dereferencing",
                    description="More than 2 levels of pointer indirection detected",
                    severity=Severity.MAJOR,
                    line_number=i,
                    suggestion="Limit pointer indirection to 2 levels maximum",
                    code_snippet=line.strip()
                ))
    
    def _check_rule_6_variable_declarations(self):
        """Rule 6: All Variables Must Be Declared at the Top of Their Scope."""
        # This is a simplified check - in practice, you'd need AST analysis
        in_function = False
        function_start = 0
        
        for i, line in enumerate(self.code_lines, 1):
            # Detect function start
            if re.match(r'\w+\s+\w+\s*\([^)]*\)\s*\{', line):
                in_function = True
                function_start = i
                continue
            
            # Check for variable declarations in middle of function
            if in_function and re.match(r'\s*(int|char|float|double|long|short|unsigned|signed)\s+\w+', line):
                if i > function_start + 2:  # Allow first few lines for declarations
                    self.violations.append(Violation(
                        rule_id="rule_6",
                        rule_name="Variable Declarations",
                        description="Variable declaration may not be at scope beginning",
                        severity=Severity.MINOR,
                        line_number=i,
                        suggestion="Move all variable declarations to beginning of scope",
                        code_snippet=line.strip()
                    ))
            
            # Detect function end
            if line.strip() == '}' and in_function:
                in_function = False
    
    def _check_rule_7_single_return(self):
        """Rule 7: All Functions Must Have a Single Return Point."""
        in_function = False
        return_count = 0
        function_start = 0
        
        for i, line in enumerate(self.code_lines, 1):
            # Detect function start
            if re.match(r'\w+\s+\w+\s*\([^)]*\)\s*\{', line):
                in_function = True
                function_start = i
                return_count = 0
                continue
            
            # Count return statements
            if in_function and 'return' in line and not line.strip().startswith('//'):
                return_count += 1
            
            # Detect function end
            if line.strip() == '}' and in_function:
                if return_count > 1:
                    self.violations.append(Violation(
                        rule_id="rule_7",
                        rule_name="Single Return Point",
                        description=f"Function with {return_count} return statements detected",
                        severity=Severity.MODERATE,
                        line_number=function_start,
                        suggestion="Use single return point with result variable",
                        code_snippet=self.code_lines[function_start-1].strip()
                    ))
                in_function = False
    
    def _check_rule_8_preprocessor(self):
        """Rule 8: No Use of Preprocessor Directives Except #include."""
        for i, line in enumerate(self.code_lines, 1):
            if line.strip().startswith('#') and not line.strip().startswith('#include'):
                self.violations.append(Violation(
                    rule_id="rule_8",
                    rule_name="Preprocessor Usage",
                    description="Preprocessor directive other than #include detected",
                    severity=Severity.MINOR,
                    line_number=i,
                    suggestion="Use const declarations instead of #define",
                    code_snippet=line.strip()
                ))
    
    def _check_rule_9_assignment_expressions(self):
        """Rule 9: No Use of Assignments in Expressions."""
        for i, line in enumerate(self.code_lines, 1):
            # Check for assignment in while/if conditions
            if re.search(r'(while|if)\s*\([^)]*=\s*[^)]*\)', line):
                self.violations.append(Violation(
                    rule_id="rule_9",
                    rule_name="Assignment in Expressions",
                    description="Assignment in conditional expression detected",
                    severity=Severity.MODERATE,
                    line_number=i,
                    suggestion="Separate assignment from condition checking",
                    code_snippet=line.strip()
                ))
    
    def _check_rule_10_multiple_assignments(self):
        """Rule 10: No Use of Multiple Assignments."""
        for i, line in enumerate(self.code_lines, 1):
            # Check for multiple assignments in single line
            if line.count('=') > 1 and '==' not in line:
                self.violations.append(Violation(
                    rule_id="rule_10",
                    rule_name="Multiple Assignments",
                    description="Multiple assignments in single statement detected",
                    severity=Severity.MINOR,
                    line_number=i,
                    suggestion="Use separate assignment statements",
                    code_snippet=line.strip()
                ))
    
    def _check_naming_conventions(self):
        """Check naming conventions."""
        for i, line in enumerate(self.code_lines, 1):
            # Check for short variable names
            var_match = re.search(r'\b(int|char|float|double)\s+([a-z]{1,2})\b', line)
            if var_match:
                var_name = var_match.group(2)
                if len(var_name) < 3:
                    self.violations.append(Violation(
                        rule_id="style_naming",
                        rule_name="Naming Conventions",
                        description=f"Variable name '{var_name}' is too short",
                        severity=Severity.MINOR,
                        line_number=i,
                        suggestion="Use descriptive variable names",
                        code_snippet=line.strip()
                    ))
    
    def _check_function_length(self):
        """Check function length."""
        in_function = False
        function_start = 0
        line_count = 0
        
        for i, line in enumerate(self.code_lines, 1):
            # Detect function start
            if re.match(r'\w+\s+\w+\s*\([^)]*\)\s*\{', line):
                in_function = True
                function_start = i
                line_count = 0
                continue
            
            if in_function:
                line_count += 1
            
            # Detect function end
            if line.strip() == '}' and in_function:
                if line_count > 50:
                    self.violations.append(Violation(
                        rule_id="style_function_length",
                        rule_name="Function Length",
                        description=f"Function is {line_count} lines long (exceeds 50 line limit)",
                        severity=Severity.MODERATE,
                        line_number=function_start,
                        suggestion="Break function into smaller functions",
                        code_snippet=self.code_lines[function_start-1].strip()
                    ))
                in_function = False
    
    def _check_comment_coverage(self):
        """Check comment coverage."""
        for i, line in enumerate(self.code_lines, 1):
            # Check for function definitions without comments
            if re.match(r'\w+\s+\w+\s*\([^)]*\)\s*\{?', line):
                # Look for comment above function
                has_comment = False
                for j in range(max(0, i-3), i):
                    if self.code_lines[j].strip().startswith('//') or self.code_lines[j].strip().startswith('/*'):
                        has_comment = True
                        break
                
                if not has_comment:
                    self.violations.append(Violation(
                        rule_id="style_comments",
                        rule_name="Comment Coverage",
                        description="Function without header comment detected",
                        severity=Severity.MINOR,
                        line_number=i,
                        suggestion="Add function header comment explaining purpose and parameters",
                        code_snippet=line.strip()
                    ))
    
    def _check_error_handling(self):
        """Check error handling patterns."""
        for i, line in enumerate(self.code_lines, 1):
            # Check for functions that don't return error codes
            if re.match(r'void\s+\w+\s*\([^)]*\)\s*\{?', line):
                # Look for error handling in void functions
                has_error_handling = False
                for j in range(i, min(i+20, len(self.code_lines))):
                    if 'error' in self.code_lines[j].lower() or 'return' in self.code_lines[j]:
                        has_error_handling = True
                        break
                
                if not has_error_handling:
                    self.violations.append(Violation(
                        rule_id="style_error_handling",
                        rule_name="Error Handling",
                        description="Void function without apparent error handling",
                        severity=Severity.MINOR,
                        line_number=i,
                        suggestion="Consider returning error codes or implementing error handling",
                        code_snippet=line.strip()
                    ))
    
    def _check_type_safety(self):
        """Check type safety."""
        for i, line in enumerate(self.code_lines, 1):
            # Check for implicit integer types
            if re.search(r'\bint\s+\w+', line) and 'stdint.h' not in '\n'.join(self.code_lines[:i]):
                self.violations.append(Violation(
                    rule_id="style_type_safety",
                    rule_name="Type Safety",
                    description="Use of implicit integer type 'int'",
                    severity=Severity.MINOR,
                    line_number=i,
                    suggestion="Use explicit integer types from stdint.h",
                    code_snippet=line.strip()
                ))
    
    def calculate_compliance_score(self) -> int:
        """Calculate overall compliance score."""
        if not self.violations:
            return 100
        
        base_score = 100
        severity_penalties = {
            Severity.MINOR: 2,
            Severity.MODERATE: 5,
            Severity.MAJOR: 10,
            Severity.CRITICAL: 15
        }
        
        for violation in self.violations:
            base_score -= severity_penalties.get(violation.severity, 5)
        
        return max(0, base_score)
    
    def get_compliance_level(self) -> str:
        """Get compliance level based on score."""
        score = self.calculate_compliance_score()
        
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
    
    def generate_report(self) -> str:
        """Generate compliance report."""
        report = []
        report.append("=" * 60)
        report.append("NASA C CODE COMPLIANCE REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        score = self.calculate_compliance_score()
        level = self.get_compliance_level()
        report.append(f"Overall Compliance Score: {score}/100")
        report.append(f"Compliance Level: {level.replace('_', ' ').title()}")
        report.append(f"Total Violations: {len(self.violations)}")
        report.append("")
        
        # Violations by severity
        if self.violations:
            severity_counts = {}
            for violation in self.violations:
                severity_counts[violation.severity] = severity_counts.get(violation.severity, 0) + 1
            
            report.append("VIOLATIONS BY SEVERITY:")
            report.append("-" * 25)
            for severity in Severity:
                count = severity_counts.get(severity, 0)
                if count > 0:
                    report.append(f"{severity.value.title()}: {count}")
            report.append("")
            
            # Detailed violations
            report.append("DETAILED VIOLATIONS:")
            report.append("-" * 25)
            for i, violation in enumerate(self.violations, 1):
                report.append(f"{i}. {violation.rule_name} (Line {violation.line_number})")
                report.append(f"   Severity: {violation.severity.value.title()}")
                report.append(f"   Description: {violation.description}")
                report.append(f"   Suggestion: {violation.suggestion}")
                if violation.code_snippet:
                    report.append(f"   Code: {violation.code_snippet}")
                report.append("")
        else:
            report.append("No rule violations detected!")
            report.append("")
        
        # Recommendations
        if self.violations:
            report.append("RECOMMENDATIONS:")
            report.append("-" * 20)
            critical_violations = [v for v in self.violations if v.severity == Severity.CRITICAL]
            if critical_violations:
                report.append("1. Address critical violations first (goto, dynamic memory, recursion)")
            major_violations = [v for v in self.violations if v.severity == Severity.MAJOR]
            if major_violations:
                report.append("2. Fix major violations (unbounded loops, excessive parameters)")
            report.append("3. Review and fix moderate and minor violations")
            report.append("4. Consider using static analysis tools for ongoing compliance")
        
        return "\n".join(report)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Check C code for NASA compliance')
    parser.add_argument('--code-file', help='Path to C code file')
    parser.add_argument('--code-string', help='C code as string')
    parser.add_argument('--output-file', help='Output file for report')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    args = parser.parse_args()
    
    if not args.code_file and not args.code_string:
        print("Error: Must provide either --code-file or --code-string")
        sys.exit(1)
    
    # Load code
    if args.code_file:
        with open(args.code_file, 'r') as f:
            code = f.read()
    else:
        code = args.code_string
    
    # Check compliance
    checker = NASAComplianceChecker()
    checker.load_code(code)
    violations = checker.check_all_rules()
    
    # Generate results
    if args.json:
        result = {
            'compliance_score': checker.calculate_compliance_score(),
            'compliance_level': checker.get_compliance_level(),
            'total_violations': len(violations),
            'violations': [
                {
                    'rule_id': v.rule_id,
                    'rule_name': v.rule_name,
                    'description': v.description,
                    'severity': v.severity.value,
                    'line_number': v.line_number,
                    'suggestion': v.suggestion,
                    'code_snippet': v.code_snippet
                }
                for v in violations
            ]
        }
        
        if args.output_file:
            with open(args.output_file, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))
    else:
        report = checker.generate_report()
        
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(report)
            print(f"Report saved to {args.output_file}")
        else:
            print(report)

if __name__ == '__main__':
    main()
