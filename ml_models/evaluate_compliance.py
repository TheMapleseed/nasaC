#!/usr/bin/env python3
"""
NASA C Code Compliance Evaluation Script

This script evaluates C code for compliance with NASA standards using
trained machine learning models.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging
import argparse

import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModel
import joblib
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

class ComplianceEvaluator:
    """Evaluates C code for NASA compliance using trained models."""
    
    def __init__(self, models_dir: str):
        self.models_dir = Path(models_dir)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load models
        self.rf_model = None
        self.nn_model = None
        self.tokenizer = None
        
        self._load_models()
    
    def _load_models(self):
        """Load trained models from disk."""
        # Load Random Forest model
        rf_path = self.models_dir / 'random_forest_model.joblib'
        if rf_path.exists():
            self.rf_model = joblib.load(rf_path)
            logger.info("Random Forest model loaded successfully")
        
        # Load Neural Network model
        nn_path = self.models_dir / 'neural_network_model.pt'
        if nn_path.exists():
            self.nn_model = ComplianceClassifier('microsoft/codebert-base')
            self.nn_model.load_state_dict(torch.load(nn_path, map_location=self.device))
            self.nn_model.to(self.device)
            self.nn_model.eval()
            self.tokenizer = AutoTokenizer.from_pretrained('microsoft/codebert-base')
            logger.info("Neural Network model loaded successfully")
    
    def extract_features(self, code: str) -> Dict[str, Any]:
        """Extract features from C code for analysis."""
        features = {
            'code_length': len(code),
            'function_count': self._count_functions(code),
            'line_count': len(code.split('\n')),
            'complexity_score': self._calculate_complexity(code),
            'nesting_depth': self._calculate_nesting_depth(code),
            'variable_count': self._count_variables(code),
            'pointer_count': self._count_pointers(code),
            'loop_count': self._count_loops(code),
            'conditional_count': self._count_conditionals(code),
            'violation_count': 0  # Will be updated by rule checking
        }
        return features
    
    def _count_functions(self, code: str) -> int:
        """Count function definitions in code."""
        import re
        # Simple regex to count function definitions
        function_pattern = r'\w+\s+\w+\s*\([^)]*\)\s*\{'
        return len(re.findall(function_pattern, code))
    
    def _calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        # Count decision points
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
    
    def _count_variables(self, code: str) -> int:
        """Count variable declarations."""
        import re
        # Count int, char, float, double, etc. declarations
        var_pattern = r'\b(int|char|float|double|long|short|unsigned|signed)\s+\w+'
        return len(re.findall(var_pattern, code))
    
    def _count_pointers(self, code: str) -> int:
        """Count pointer operations."""
        import re
        # Count pointer dereferences and declarations
        ptr_pattern = r'\*+\w+|\w+\s*\*+\s*\w+'
        return len(re.findall(ptr_pattern, code))
    
    def _count_loops(self, code: str) -> int:
        """Count loop constructs."""
        import re
        loop_pattern = r'\b(for|while|do)\b'
        return len(re.findall(loop_pattern, code))
    
    def _count_conditionals(self, code: str) -> int:
        """Count conditional statements."""
        import re
        cond_pattern = r'\b(if|else|switch|case)\b'
        return len(re.findall(cond_pattern, code))
    
    def check_power_of_10_rules(self, code: str) -> List[Dict[str, Any]]:
        """Check code against NASA Power of 10 rules."""
        violations = []
        
        # Rule 1: Avoid Complex Flow Control
        if 'goto' in code:
            violations.append({
                'rule_id': 'rule_1',
                'rule_name': 'Avoid Complex Flow Control',
                'description': 'Use of goto statement detected',
                'severity': 'critical',
                'suggestion': 'Replace goto with structured control flow'
            })
        
        if 'setjmp' in code or 'longjmp' in code:
            violations.append({
                'rule_id': 'rule_1',
                'rule_name': 'Avoid Complex Flow Control',
                'description': 'Use of setjmp/longjmp detected',
                'severity': 'critical',
                'suggestion': 'Use structured error handling instead'
            })
        
        # Rule 2: Fixed Loop Bounds
        import re
        while_pattern = r'while\s*\([^)]*\)\s*\{'
        while_matches = re.findall(while_pattern, code)
        for match in while_matches:
            if 'MAX_' not in match and 'count' not in match:
                violations.append({
                    'rule_id': 'rule_2',
                    'rule_name': 'Fixed Loop Bounds',
                    'description': 'Loop without clear upper bound detected',
                    'severity': 'major',
                    'suggestion': 'Add compile-time determinable upper bound'
                })
        
        # Rule 3: No Dynamic Memory
        if 'malloc' in code or 'free' in code:
            violations.append({
                'rule_id': 'rule_3',
                'rule_name': 'No Dynamic Memory',
                'description': 'Dynamic memory allocation detected',
                'severity': 'critical',
                'suggestion': 'Use static allocation or stack-based allocation'
            })
        
        # Rule 4: Function Parameters
        import re
        func_pattern = r'\w+\s+\w+\s*\(([^)]*)\)'
        func_matches = re.findall(func_pattern, code)
        for params in func_matches:
            param_count = len([p.strip() for p in params.split(',') if p.strip()])
            if param_count > 2:
                violations.append({
                    'rule_id': 'rule_4',
                    'rule_name': 'Function Parameters',
                    'description': f'Function with {param_count} parameters detected',
                    'severity': 'major',
                    'suggestion': 'Use structure to group related parameters'
                })
        
        # Rule 5: Pointer Dereferencing
        if '***' in code:
            violations.append({
                'rule_id': 'rule_5',
                'rule_name': 'Pointer Dereferencing',
                'description': 'More than 2 levels of pointer indirection detected',
                'severity': 'major',
                'suggestion': 'Limit pointer indirection to 2 levels maximum'
            })
        
        # Rule 6: Variable Declarations
        # This is harder to detect automatically, but we can look for patterns
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if 'int ' in line or 'char ' in line or 'float ' in line:
                if i > 0 and not lines[i-1].strip().startswith('//'):
                    # Check if this might be a declaration in the middle
                    violations.append({
                        'rule_id': 'rule_6',
                        'rule_name': 'Variable Declarations',
                        'description': 'Variable declaration may not be at scope beginning',
                        'severity': 'minor',
                        'suggestion': 'Move all variable declarations to beginning of scope'
                    })
                    break
        
        # Rule 7: Single Return Point
        import re
        return_pattern = r'\breturn\s+[^;]+;'
        return_matches = re.findall(return_pattern, code)
        if len(return_matches) > 1:
            violations.append({
                'rule_id': 'rule_7',
                'rule_name': 'Single Return Point',
                'description': 'Multiple return statements detected',
                'severity': 'moderate',
                'suggestion': 'Use single return point with result variable'
            })
        
        # Rule 8: Preprocessor Usage
        if '#define' in code:
            violations.append({
                'rule_id': 'rule_8',
                'rule_name': 'Preprocessor Usage',
                'description': 'Use of #define directive detected',
                'severity': 'minor',
                'suggestion': 'Use const declarations instead of #define'
            })
        
        # Rule 9: Assignment in Expressions
        import re
        assign_pattern = r'while\s*\([^)]*=\s*[^)]*\)|if\s*\([^)]*=\s*[^)]*\)'
        if re.search(assign_pattern, code):
            violations.append({
                'rule_id': 'rule_9',
                'rule_name': 'Assignment in Expressions',
                'description': 'Assignment in conditional expression detected',
                'severity': 'moderate',
                'suggestion': 'Separate assignment from condition checking'
            })
        
        # Rule 10: Multiple Assignments
        if '=' in code and code.count('=') > 1:
            # Check for multiple assignments in single line
            lines = code.split('\n')
            for line in lines:
                if line.count('=') > 1 and '==' not in line:
                    violations.append({
                        'rule_id': 'rule_10',
                        'rule_name': 'Multiple Assignments',
                        'description': 'Multiple assignments in single statement detected',
                        'severity': 'minor',
                        'suggestion': 'Use separate assignment statements'
                    })
                    break
        
        return violations
    
    def predict_compliance(self, code: str) -> Dict[str, Any]:
        """Predict compliance using trained models."""
        features = self.extract_features(code)
        violations = self.check_power_of_10_rules(code)
        
        # Update violation count
        features['violation_count'] = len(violations)
        
        # Calculate base compliance score
        base_score = 100
        for violation in violations:
            severity_multipliers = {'minor': 1.0, 'moderate': 1.5, 'major': 2.0, 'critical': 3.0}
            penalty = severity_multipliers.get(violation['severity'], 1.0) * 5
            base_score -= penalty
        
        compliance_score = max(0, base_score)
        
        # Determine compliance level
        if compliance_score >= 90:
            compliance_level = 'fully_compliant'
        elif compliance_score >= 80:
            compliance_level = 'minor_issues'
        elif compliance_score >= 70:
            compliance_level = 'moderate_issues'
        elif compliance_score >= 60:
            compliance_level = 'major_issues'
        else:
            compliance_level = 'non_compliant'
        
        # Use ML models for prediction if available
        ml_score = None
        ml_level = None
        
        if self.rf_model:
            # Random Forest prediction
            feature_df = pd.DataFrame([features])
            X = feature_df.drop('violation_count', axis=1)
            ml_score = self.rf_model.predict(X)[0]
        
        if self.nn_model and self.tokenizer:
            # Neural Network prediction
            try:
                encoding = self.tokenizer(
                    code,
                    truncation=True,
                    padding='max_length',
                    max_length=512,
                    return_tensors='pt'
                )
                
                with torch.no_grad():
                    input_ids = encoding['input_ids'].to(self.device)
                    attention_mask = encoding['attention_mask'].to(self.device)
                    
                    classification_logits, regression_score = self.nn_model(input_ids, attention_mask)
                    ml_level = torch.argmax(classification_logits, dim=1).item()
                    ml_score = regression_score.item() * 100
            except Exception as e:
                logger.warning(f"Neural network prediction failed: {e}")
        
        return {
            'compliance_score': compliance_score,
            'compliance_level': compliance_level,
            'violations': violations,
            'features': features,
            'ml_score': ml_score,
            'ml_level': ml_level
        }
    
    def generate_report(self, code: str, result: Dict[str, Any]) -> str:
        """Generate a detailed compliance report."""
        report = []
        report.append("=" * 60)
        report.append("NASA C CODE COMPLIANCE REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append(f"Overall Compliance Score: {result['compliance_score']}/100")
        report.append(f"Compliance Level: {result['compliance_level'].replace('_', ' ').title()}")
        report.append(f"Total Violations: {len(result['violations'])}")
        report.append("")
        
        # ML Model Predictions
        if result['ml_score'] is not None:
            report.append(f"ML Model Score: {result['ml_score']:.1f}/100")
        if result['ml_level'] is not None:
            level_names = ['Fully Compliant', 'Minor Issues', 'Moderate Issues', 'Major Issues', 'Non-Compliant']
            report.append(f"ML Model Level: {level_names[result['ml_level']]}")
        report.append("")
        
        # Violations
        if result['violations']:
            report.append("RULE VIOLATIONS:")
            report.append("-" * 30)
            for i, violation in enumerate(result['violations'], 1):
                report.append(f"{i}. {violation['rule_name']} (Severity: {violation['severity']})")
                report.append(f"   Description: {violation['description']}")
                report.append(f"   Suggestion: {violation['suggestion']}")
                report.append("")
        else:
            report.append("No rule violations detected!")
            report.append("")
        
        # Code Statistics
        report.append("CODE STATISTICS:")
        report.append("-" * 20)
        features = result['features']
        report.append(f"Lines of Code: {features['line_count']}")
        report.append(f"Functions: {features['function_count']}")
        report.append(f"Complexity Score: {features['complexity_score']}")
        report.append(f"Nesting Depth: {features['nesting_depth']}")
        report.append(f"Variables: {features['variable_count']}")
        report.append(f"Pointers: {features['pointer_count']}")
        report.append(f"Loops: {features['loop_count']}")
        report.append(f"Conditionals: {features['conditional_count']}")
        
        return "\n".join(report)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Evaluate C code for NASA compliance')
    parser.add_argument('--code-file', help='Path to C code file')
    parser.add_argument('--code-string', help='C code as string')
    parser.add_argument('--models-dir', default='./trained_models', help='Directory containing trained models')
    parser.add_argument('--output-file', help='Output file for report')
    
    args = parser.parse_args()
    
    if not args.code_file and not args.code_string:
        console.print("[red]Error: Must provide either --code-file or --code-string[/red]")
        sys.exit(1)
    
    # Load code
    if args.code_file:
        with open(args.code_file, 'r') as f:
            code = f.read()
    else:
        code = args.code_string
    
    # Initialize evaluator
    evaluator = ComplianceEvaluator(args.models_dir)
    
    # Evaluate compliance
    result = evaluator.predict_compliance(code)
    
    # Generate report
    report = evaluator.generate_report(code, result)
    
    # Display results
    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(report)
        console.print(f"[green]Report saved to {args.output_file}[/green]")
    else:
        console.print(report)
    
    # Display summary in rich format
    table = Table(title="Compliance Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Compliance Score", f"{result['compliance_score']}/100")
    table.add_row("Compliance Level", result['compliance_level'].replace('_', ' ').title())
    table.add_row("Violations", str(len(result['violations'])))
    table.add_row("Functions", str(result['features']['function_count']))
    table.add_row("Lines of Code", str(result['features']['line_count']))
    
    console.print(table)

if __name__ == '__main__':
    main()
