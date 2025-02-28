"""
AIDevOS Code Review Module
This module provides code review tools for ensuring code quality and security.
"""

import os
import re
import json
import subprocess
from typing import Dict, List, Any, Optional


class CodeReviewer:
    """Performs automated code reviews"""
    
    def __init__(self, repo_path: str):
        """
        Initialize the code reviewer
        
        Args:
            repo_path: Path to the code repository
        """
        self.repo_path = repo_path
        
    def check_code_style(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Check the style of a Python file
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            List of style issues
        """
        issues = []
        
        # Style patterns to check for
        style_patterns = {
            "Line Length": {
                "pattern": r'^.{100,}$',
                "message": "Line exceeds 100 characters",
                "severity": "LOW"
            },
            "Missing Docstring": {
                "pattern": r'^\s*(?:def|class)\s+\w+\s*(?:\(.*\))?\s*:(?!\s*["\'])(?!\s*r?["\'])(?!\s*r?["\'\'])(?!\s*u?["\'])(?!\s*u?["\'\'])(?!\s*ur?["\'])(?!\s*ur?["\'\'])(?!\s*r?u["\'])(?!\s*r?u["\'\'])',
                "message": "Missing docstring for function or class",
                "severity": "MEDIUM"
            },
            "Import Not At Top": {
                "pattern": r'^\s*def.*:\s*\n\s+import',
                "message": "Import not at the top of the file",
                "severity": "LOW"
            },
            "Too Many Blank Lines": {
                "pattern": r'\n\s*\n\s*\n\s*\n',
                "message": "Too many consecutive blank lines",
                "severity": "LOW"
            },
            "Mixed Tabs and Spaces": {
                "pattern": r'^\t+ +|\s+\t+',
                "message": "Mixed tabs and spaces for indentation",
                "severity": "MEDIUM"
            }
        }
        
        try:
            with open(os.path.join(self.repo_path, file_path), 'r') as f:
                content = f.readlines()
                file_content = ''.join(content)
                
                # Check whole file patterns
                for pattern_name, pattern_info in style_patterns.items():
                    if "Too Many Blank Lines" in pattern_name or "Import Not At Top" in pattern_name:
                        matches = re.findall(pattern_info["pattern"], file_content, re.MULTILINE)
                        if matches:
                            issues.append({
                                "file": file_path,
                                "line": "N/A",
                                "type": pattern_name,
                                "message": pattern_info["message"],
                                "severity": pattern_info["severity"]
                            })
                
                # Check line by line patterns
                for line_number, line in enumerate(content, 1):
                    for pattern_name, pattern_info in style_patterns.items():
                        if "Too Many Blank Lines" not in pattern_name and "Import Not At Top" not in pattern_name:
                            if re.search(pattern_info["pattern"], line):
                                issues.append({
                                    "file": file_path,
                                    "line": line_number,
                                    "type": pattern_name,
                                    "message": pattern_info["message"],
                                    "severity": pattern_info["severity"]
                                })
        except Exception as e:
            print(f"Error checking style for {file_path}: {e}")
        
        return issues
    
    def check_code_complexity(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Check the complexity of a Python file
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            List of complexity issues
        """
        issues = []
        
        try:
            # These would normally be calculated using a tool like radon or mccabe
            # This is a simplified mock implementation
            with open(os.path.join(self.repo_path, file_path), 'r') as f:
                content = f.readlines()
                
                function_pattern = r'def\s+(\w+)\s*\('
                class_pattern = r'class\s+(\w+)\s*'
                nested_blocks = r'^\s+(?:if|for|while|with|try|def)\s+'
                
                functions = []
                classes = []
                
                # Find functions and classes
                for line_number, line in enumerate(content, 1):
                    func_match = re.search(function_pattern, line)
                    if func_match:
                        functions.append((func_match.group(1), line_number))
                        
                    class_match = re.search(class_pattern, line)
                    if class_match:
                        classes.append((class_match.group(1), line_number))
                
                # Check function complexity
                for func_name, line_number in functions:
                    # Count the number of nested blocks
                    nested_count = 0
                    in_function = False
                    func_indent = None
                    
                    for i, line in enumerate(content[line_number-1:], line_number):
                        # Determine function indentation level
                        if i == line_number:
                            func_indent = len(line) - len(line.lstrip())
                            in_function = True
                            continue
                        
                        # Skip if not in the function
                        if not in_function:
                            continue
                        
                        # Check if we've moved out of the function
                        line_indent = len(line) - len(line.lstrip())
                        if line_indent <= func_indent and line.strip():
                            in_function = False
                            break
                        
                        # Count nested blocks
                        if re.search(nested_blocks, line):
                            nested_count += 1
                    
                    # Flag complex functions
                    if nested_count > 3:
                        issues.append({
                            "file": file_path,
                            "line": line_number,
                            "type": "Complex Function",
                            "message": f"Function '{func_name}' has high cyclomatic complexity ({nested_count} nested blocks)",
                            "severity": "MEDIUM"
                        })
                
                # Check long functions
                for func_name, line_number in functions:
                    # Count the number of lines in the function
                    line_count = 0
                    in_function = False
                    func_indent = None
                    
                    for i, line in enumerate(content[line_number-1:], line_number):
                        # Determine function indentation level
                        if i == line_number:
                            func_indent = len(line) - len(line.lstrip())
                            in_function = True
                            continue
                        
                        # Skip if not in the function
                        if not in_function:
                            continue
                        
                        # Check if we've moved out of the function
                        line_indent = len(line) - len(line.lstrip())
                        if line_indent <= func_indent and line.strip():
                            in_function = False
                            break
                        
                        # Count lines
                        if line.strip():
                            line_count += 1
                    
                    # Flag long functions
                    if line_count > 50:
                        issues.append({
                            "file": file_path,
                            "line": line_number,
                            "type": "Long Function",
                            "message": f"Function '{func_name}' is too long ({line_count} lines)",
                            "severity": "MEDIUM"
                        })
        except Exception as e:
            print(f"Error checking complexity for {file_path}: {e}")
        
        return issues
    
    def check_for_anti_patterns(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Check for anti-patterns in a Python file
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            List of anti-pattern issues
        """
        issues = []
        
        # Anti-pattern patterns to check for
        anti_patterns = {
            "Global Variable": {
                "pattern": r'^(?!def|class|import|from|#|\s*\"\"\"|\s*[\'"]|$).*=',
                "message": "Use of global variable",
                "severity": "MEDIUM"
            },
            "Magic Number": {
                "pattern": r'[=!<>]=?\s*(?!0|1|-1|True|False|None)[0-9]{2,}',
                "message": "Use of magic number - consider using a named constant",
                "severity": "LOW"
            },
            "Bare Except": {
                "pattern": r'except\s*:',
                "message": "Use of bare except clause - specify exceptions to catch",
                "severity": "HIGH"
            },
            "Mutable Default Argument": {
                "pattern": r'def\s+\w+\s*\(.*=\s*(?:\[\]|{}|\{\}|dict\(\)|list\(\)|set\(\))',
                "message": "Use of mutable default argument",
                "severity": "MEDIUM"
            },
            "Star Import": {
                "pattern": r'from\s+\w+\s+import\s+\*',
                "message": "Use of star import - import specific names instead",
                "severity": "MEDIUM"
            }
        }
        
        try:
            with open(os.path.join(self.repo_path, file_path), 'r') as f:
                content = f.readlines()
                
                for line_number, line in enumerate(content, 1):
                    for pattern_name, pattern_info in anti_patterns.items():
                        if re.search(pattern_info["pattern"], line):
                            issues.append({
                                "file": file_path,
                                "line": line_number,
                                "type": pattern_name,
                                "message": pattern_info["message"],
                                "severity": pattern_info["severity"]
                            })
        except Exception as e:
            print(f"Error checking for anti-patterns in {file_path}: {e}")
        
        return issues
    
    def generate_review_report(self, output_file: str = "code_review_report.json") -> Dict[str, Any]:
        """
        Generate a comprehensive code review report
        
        Args:
            output_file: Path to write the report JSON
            
        Returns:
            Report data as a dictionary
        """
        # Get all Python files in the repo
        python_files = []
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py'):
                    rel_path = os.path.relpath(os.path.join(root, file), self.repo_path)
                    python_files.append(rel_path)
        
        # Scan each file
        all_style_issues = []
        all_complexity_issues = []
        all_anti_pattern_issues = []
        
        for file_path in python_files:
            style_issues = self.check_code_style(file_path)
            complexity_issues = self.check_code_complexity(file_path)
            anti_pattern_issues = self.check_for_anti_patterns(file_path)
            
            all_style_issues.extend(style_issues)
            all_complexity_issues.extend(complexity_issues)
            all_anti_pattern_issues.extend(anti_pattern_issues)
        
        # Compile report
        report = {
            "summary": {
                "style_issue_count": len(all_style_issues),
                "complexity_issue_count": len(all_complexity_issues),
                "anti_pattern_issue_count": len(all_anti_pattern_issues),
                "total_issues": len(all_style_issues) + len(all_complexity_issues) + len(all_anti_pattern_issues)
            },
            "style_issues": all_style_issues,
            "complexity_issues": all_complexity_issues,
            "anti_pattern_issues": all_anti_pattern_issues
        }
        
        # Write report to file
        with open(os.path.join(self.repo_path, output_file), 'w') as f:
            json.dump(report, f, indent=2)
        
        return report