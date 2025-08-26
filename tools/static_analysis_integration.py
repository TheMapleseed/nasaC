#!/usr/bin/env python3
"""
Static Analysis Integration for NASA C Code Compliance

This tool integrates with industry-standard static analysis tools to provide
comprehensive compliance checking and enhance ML training data quality.
"""

import subprocess
import json
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StaticAnalysisResult:
    """Result from static analysis tool."""
    tool_name: str
    file_path: str
    line_number: int
    severity: str
    message: str
    rule_id: str
    category: str
    confidence: float

class StaticAnalysisIntegrator:
    """Integrates multiple static analysis tools for comprehensive compliance checking."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tools = {
            'cppcheck': self._check_cppcheck_available(),
            'clang_tidy': self._check_clang_tidy_available(),
            'splint': self._check_splint_available(),
            'flawfinder': self._check_flawfinder_available()
        }
        
        logger.info(f"Available static analysis tools: {list(self.tools.keys())}")
    
    def _check_cppcheck_available(self) -> bool:
        """Check if cppcheck is available."""
        try:
            result = subprocess.run(['cppcheck', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_clang_tidy_available(self) -> bool:
        """Check if clang-tidy is available."""
        try:
            result = subprocess.run(['clang-tidy', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_splint_available(self) -> bool:
        """Check if splint is available."""
        try:
            result = subprocess.run(['splint', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_flawfinder_available(self) -> bool:
        """Check if flawfinder is available."""
        try:
            result = subprocess.run(['flawfinder', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def run_cppcheck(self, file_path: str) -> List[StaticAnalysisResult]:
        """Run cppcheck on a C file."""
        if not self.tools['cppcheck']:
            logger.warning("cppcheck not available")
            return []
        
        results = []
        try:
            # Run cppcheck with comprehensive checks
            cmd = [
                'cppcheck',
                '--enable=all',           # Enable all checks
                '--xml',                  # XML output
                '--xml-version=2',        # XML version 2
                '--suppress=missingIncludeSystem',  # Suppress system include warnings
                '--suppress=unusedFunction',        # Suppress unused function warnings
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 or result.returncode == 1:  # cppcheck returns 1 for warnings
                # Parse XML output
                results = self._parse_cppcheck_xml(result.stdout, file_path)
            
        except subprocess.TimeoutExpired:
            logger.error(f"cppcheck timed out for {file_path}")
        except Exception as e:
            logger.error(f"cppcheck error for {file_path}: {e}")
        
        return results
    
    def run_clang_tidy(self, file_path: str) -> List[StaticAnalysisResult]:
        """Run clang-tidy on a C file."""
        if not self.tools['clang_tidy']:
            logger.warning("clang-tidy not available")
            return []
        
        results = []
        try:
            # Run clang-tidy with comprehensive checks
            cmd = [
                'clang-tidy',
                '--checks=*',            # All checks
                '--warnings-as-errors=*', # Treat warnings as errors
                '--format-style=json',    # JSON output
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 or result.returncode == 1:  # clang-tidy returns 1 for warnings
                # Parse JSON output
                results = self._parse_clang_tidy_json(result.stdout, file_path)
            
        except subprocess.TimeoutExpired:
            logger.error(f"clang-tidy timed out for {file_path}")
        except Exception as e:
            logger.error(f"clang-tidy error for {file_path}: {e}")
        
        return results
    
    def run_splint(self, file_path: str) -> List[StaticAnalysisResult]:
        """Run splint on a C file."""
        if not self.tools['splint']:
            logger.warning("splint not available")
            return []
        
        results = []
        try:
            # Run splint with comprehensive checks
            cmd = [
                'splint',
                '+all',                  # All checks
                '+bounds',               # Array bounds checking
                '+strict',               # Strict checking
                '+unrecog',             # Unrecognized identifier checking
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 or result.returncode == 1:  # splint returns 1 for warnings
                # Parse text output
                results = self._parse_splint_output(result.stdout, file_path)
            
        except subprocess.TimeoutExpired:
            logger.error(f"splint timed out for {file_path}")
        except Exception as e:
            logger.error(f"splint error for {file_path}: {e}")
        
        return results
    
    def run_flawfinder(self, file_path: str) -> List[StaticAnalysisResult]:
        """Run flawfinder on a C file."""
        if not self.tools['flawfinder']:
            logger.warning("flawfinder not available")
            return []
        
        results = []
        try:
            # Run flawfinder with comprehensive checks
            cmd = [
                'flawfinder',
                '--html',                # HTML output
                '--context',             # Show context
                '--minlevel', '1',       # Minimum risk level
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Parse HTML output
                results = self._parse_flawfinder_html(result.stdout, file_path)
            
        except subprocess.TimeoutExpired:
            logger.error(f"flawfinder timed out for {file_path}")
        except Exception as e:
            logger.error(f"flawfinder error for {file_path}: {e}")
        
        return results
    
    def _parse_cppcheck_xml(self, xml_output: str, file_path: str) -> List[StaticAnalysisResult]:
        """Parse cppcheck XML output."""
        results = []
        
        # Simple XML parsing for cppcheck output
        # In production, use proper XML parser
        error_pattern = r'<error id="([^"]+)" severity="([^"]+)" msg="([^"]+)" verbose="[^"]*" cwe="[^"]*">'
        location_pattern = r'<location file="[^"]*" line="(\d+)" column="[^"]*"'
        
        for match in re.finditer(error_pattern, xml_output):
            rule_id = match.group(1)
            severity = match.group(2)
            message = match.group(3)
            
            # Find corresponding location
            location_match = re.search(location_pattern, xml_output[match.start():])
            line_number = int(location_match.group(1)) if location_match else 0
            
            # Map cppcheck rules to NASA/MISRA/JPL standards
            nasa_rule = self._map_cppcheck_to_nasa(rule_id)
            
            results.append(StaticAnalysisResult(
                tool_name='cppcheck',
                file_path=file_path,
                line_number=line_number,
                severity=severity,
                message=message,
                rule_id=rule_id,
                category=nasa_rule,
                confidence=0.9
            ))
        
        return results
    
    def _parse_clang_tidy_json(self, json_output: str, file_path: str) -> List[StaticAnalysisResult]:
        """Parse clang-tidy JSON output."""
        results = []
        
        try:
            data = json.loads(json_output)
            
            for diagnostic in data:
                if 'diagnostics' in diagnostic:
                    for diag in diagnostic['diagnostics']:
                        # Map clang-tidy rules to NASA/MISRA/JPL standards
                        nasa_rule = self._map_clang_tidy_to_nasa(diag.get('check_name', ''))
                        
                        results.append(StaticAnalysisResult(
                            tool_name='clang-tidy',
                            file_path=file_path,
                            line_number=diag.get('line', 0),
                            severity=diag.get('level', 'warning'),
                            message=diag.get('message', ''),
                            rule_id=diag.get('check_name', ''),
                            category=nasa_rule,
                            confidence=0.85
                        ))
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse clang-tidy JSON output for {file_path}")
        
        return results
    
    def _parse_splint_output(self, text_output: str, file_path: str) -> List[StaticAnalysisResult]:
        """Parse splint text output."""
        results = []
        
        # Parse splint output format
        # Format: file:line: message
        line_pattern = r'([^:]+):(\d+):\s*(.+)'
        
        for match in re.finditer(line_pattern, text_output):
            line_number = int(match.group(2))
            message = match.group(3)
            
            # Map splint rules to NASA/MISRA/JPL standards
            nasa_rule = self._map_splint_to_nasa(message)
            
            results.append(StaticAnalysisResult(
                tool_name='splint',
                file_path=file_path,
                line_number=line_number,
                severity='warning',
                message=message,
                rule_id='splint',
                category=nasa_rule,
                confidence=0.8
            ))
        
        return results
    
    def _parse_flawfinder_html(self, html_output: str, file_path: str) -> List[StaticAnalysisResult]:
        """Parse flawfinder HTML output."""
        results = []
        
        # Parse flawfinder HTML output
        # Look for risk patterns
        risk_pattern = r'Risk level (\d+):\s*([^<]+)'
        
        for match in re.finditer(risk_pattern, html_output):
            risk_level = int(match.group(1))
            description = match.group(2)
            
            # Map flawfinder patterns to NASA/MISRA/JPL standards
            nasa_rule = self._map_flawfinder_to_nasa(description)
            
            results.append(StaticAnalysisResult(
                tool_name='flawfinder',
                file_path=file_path,
                line_number=0,  # flawfinder doesn't always provide line numbers
                severity=f'risk_level_{risk_level}',
                message=description,
                rule_id='flawfinder',
                category=nasa_rule,
                confidence=0.75
            ))
        
        return results
    
    def _map_cppcheck_to_nasa(self, rule_id: str) -> str:
        """Map cppcheck rules to NASA coding standards."""
        mapping = {
            'unusedFunction': 'style_unused_code',
            'missingInclude': 'style_includes',
            'unusedVariable': 'style_unused_code',
            'unreadVariable': 'style_unused_code',
            'unassignedVariable': 'rule_6',
            'nullPointer': 'rule_5',
            'arrayIndexOutOfBounds': 'style_bounds_checking',
            'memoryLeak': 'rule_3',
            'resourceLeak': 'rule_3',
            'useInitializationList': 'rule_6',
            'variableScope': 'rule_6',
            'redundantAssignment': 'rule_10',
            'redundantCondition': 'style_logic',
            'redundantPointerOp': 'rule_5',
            'stlSize': 'style_containers',
            'stlBoundaries': 'style_bounds_checking',
            'stlStrFind': 'style_strings',
            'stlStrVar': 'style_strings',
            'stlStrConcat': 'style_strings',
            'stlStrSize': 'style_strings'
        }
        
        return mapping.get(rule_id, 'style_general')
    
    def _map_clang_tidy_to_nasa(self, rule_id: str) -> str:
        """Map clang-tidy rules to NASA coding standards."""
        mapping = {
            'bugprone-assignment-in-if-condition': 'rule_9',
            'bugprone-branch-clone': 'style_logic',
            'bugprone-dangling-handle': 'rule_5',
            'bugprone-dynamic-static-initializers': 'rule_3',
            'bugprone-exception-escape': 'rule_1',
            'bugprone-fold-init-type': 'style_types',
            'bugprone-forward-declaration-namespace': 'style_includes',
            'bugprone-forwarding-reference-overload': 'style_functions',
            'bugprone-inaccurate-erase': 'style_containers',
            'bugprone-infinite-loop': 'rule_2',
            'bugprone-integer-division': 'style_arithmetic',
            'bugprone-lambda-function-name': 'style_functions',
            'bugprone-macro-parentheses': 'rule_8',
            'bugprone-macro-repeated-side-effects': 'rule_8',
            'bugprone-misplaced-operator-new': 'rule_3',
            'bugprone-misplaced-pointer-arithmetic-in-alloc': 'rule_3',
            'bugprone-misplaced-widening-cast': 'style_types',
            'bugprone-move-forwarding-reference': 'style_functions',
            'bugprone-multiple-statement-macro': 'rule_8',
            'bugprone-no-escape': 'style_security',
            'bugprone-not-null-terminated-result': 'style_strings',
            'bugprone-parent-virtual-call': 'style_inheritance',
            'bugprone-posix-return': 'style_functions',
            'bugprone-reserved-identifier': 'style_naming',
            'bugprone-sizeof-container': 'style_containers',
            'bugprone-sizeof-expression': 'style_types',
            'bugprone-spuriously-missing-initialization': 'rule_6',
            'bugprone-string-constructor': 'style_strings',
            'bugprone-string-integer-assignment': 'style_types',
            'bugprone-string-literal-with-embedded-nul': 'style_strings',
            'bugprone-suspicious-enum-usage': 'style_enums',
            'bugprone-suspicious-missing-comma': 'style_syntax',
            'bugprone-suspicious-semicolon': 'style_syntax',
            'bugprone-suspicious-string-compare': 'style_strings',
            'bugprone-swapped-arguments': 'style_functions',
            'bugprone-terminating-continue': 'rule_1',
            'bugprone-throw-keyword-missing': 'style_exceptions',
            'bugprone-too-small-loop-variable': 'style_types',
            'bugprone-undefined-behavior': 'style_undefined',
            'bugprone-undelegated-constructor': 'style_classes',
            'bugprone-unhandled-self-move': 'style_moves',
            'bugprone-unused-raii': 'style_resources',
            'bugprone-unused-return-value': 'style_functions',
            'bugprone-use-after-move': 'style_moves',
            'bugprone-virtual-near-miss': 'style_inheritance'
        }
        
        return mapping.get(rule_id, 'style_general')
    
    def _map_splint_to_nasa(self, message: str) -> str:
        """Map splint messages to NASA coding standards."""
        message_lower = message.lower()
        
        if 'uninitialized' in message_lower:
            return 'rule_6'
        elif 'null pointer' in message_lower:
            return 'rule_5'
        elif 'memory leak' in message_lower:
            return 'rule_3'
        elif 'array bounds' in message_lower:
            return 'style_bounds_checking'
        elif 'unused' in message_lower:
            return 'style_unused_code'
        elif 'type' in message_lower:
            return 'style_types'
        else:
            return 'style_general'
    
    def _map_flawfinder_to_nasa(self, description: str) -> str:
        """Map flawfinder patterns to NASA coding standards."""
        desc_lower = description.lower()
        
        if 'buffer overflow' in desc_lower:
            return 'style_bounds_checking'
        elif 'format string' in desc_lower:
            return 'style_security'
        elif 'race condition' in desc_lower:
            return 'style_concurrency'
        elif 'command injection' in desc_lower:
            return 'style_security'
        else:
            return 'style_security'
    
    def run_all_tools(self, file_path: str) -> Dict[str, List[StaticAnalysisResult]]:
        """Run all available static analysis tools on a file."""
        results = {}
        
        if self.tools['cppcheck']:
            results['cppcheck'] = self.run_cppcheck(file_path)
        
        if self.tools['clang_tidy']:
            results['clang_tidy'] = self.run_clang_tidy(file_path)
        
        if self.tools['splint']:
            results['splint'] = self.run_splint(file_path)
        
        if self.tools['flawfinder']:
            results['flawfinder'] = self.run_flawfinder(file_path)
        
        return results
    
    def generate_compliance_report(self, results: Dict[str, List[StaticAnalysisResult]]) -> str:
        """Generate a comprehensive compliance report."""
        report = []
        report.append("=" * 60)
        report.append("STATIC ANALYSIS COMPLIANCE REPORT")
        report.append("=" * 60)
        report.append("")
        
        total_violations = sum(len(tool_results) for tool_results in results.values())
        report.append(f"Total Violations Found: {total_violations}")
        report.append("")
        
        # Summary by tool
        report.append("VIOLATIONS BY TOOL:")
        report.append("-" * 25)
        for tool_name, tool_results in results.items():
            report.append(f"{tool_name}: {len(tool_results)} violations")
        report.append("")
        
        # Summary by category
        category_counts = {}
        for tool_results in results.values():
            for result in tool_results:
                category = result.category
                category_counts[category] = category_counts.get(category, 0) + 1
        
        report.append("VIOLATIONS BY CATEGORY:")
        report.append("-" * 25)
        for category, count in sorted(category_counts.items()):
            report.append(f"{category}: {count} violations")
        report.append("")
        
        # Detailed violations
        if total_violations > 0:
            report.append("DETAILED VIOLATIONS:")
            report.append("-" * 25)
            
            for tool_name, tool_results in results.items():
                if tool_results:
                    report.append(f"\n{tool_name.upper()} VIOLATIONS:")
                    for i, result in enumerate(tool_results, 1):
                        report.append(f"  {i}. Line {result.line_number}: {result.message}")
                        report.append(f"     Category: {result.category}")
                        report.append(f"     Severity: {result.severity}")
                        report.append(f"     Confidence: {result.confidence:.2f}")
                        report.append("")
        else:
            report.append("No violations detected!")
            report.append("")
        
        return "\n".join(report)
    
    def export_results_json(self, results: Dict[str, List[StaticAnalysisResult]]) -> str:
        """Export results in JSON format for ML training."""
        export_data = {
            'file_path': list(results.values())[0][0].file_path if any(results.values()) else '',
            'analysis_timestamp': str(Path().absolute()),
            'tools_used': list(results.keys()),
            'total_violations': sum(len(tool_results) for tool_results in results.values()),
            'results_by_tool': {}
        }
        
        for tool_name, tool_results in results.items():
            export_data['results_by_tool'][tool_name] = [
                {
                    'line_number': result.line_number,
                    'severity': result.severity,
                    'message': result.message,
                    'rule_id': result.rule_id,
                    'category': result.category,
                    'confidence': result.confidence
                }
                for result in tool_results
            ]
        
        return json.dumps(export_data, indent=2)

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run static analysis tools for NASA compliance')
    parser.add_argument('--file', required=True, help='C file to analyze')
    parser.add_argument('--output', help='Output file for report')
    parser.add_argument('--json', action='store_true', help='Export results in JSON format')
    parser.add_argument('--config', default='./static_analysis_config.json', help='Configuration file')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Initialize integrator
    integrator = StaticAnalysisIntegrator(config)
    
    # Run analysis
    results = integrator.run_all_tools(args.file)
    
    # Generate report
    report = integrator.generate_compliance_report(results)
    
    # Output results
    if args.json:
        json_output = integrator.export_results_json(results)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(json_output)
        else:
            print(json_output)
    else:
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
        else:
            print(report)

if __name__ == '__main__':
    main()
