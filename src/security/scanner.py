"""
AIDevOS Security Scanner
This module provides security scanning capabilities to identify vulnerabilities.
"""

import os
import re
import json
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime


class VulnerabilityScanner:
    """Scans code for security vulnerabilities"""
    
    def __init__(self, repo_path: str):
        """
        Initialize the vulnerability scanner
        
        Args:
            repo_path: Path to the code repository
        """
        self.repo_path = repo_path
        
    def scan_for_secrets(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Scan a file for potential secrets
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            List of detected secrets with line numbers and patterns
        """
        secrets = []
        
        # Patterns to detect secrets
        secret_patterns = {
            "API Key": r'api[_-]?key[^a-zA-Z0-9]+(["\'`])[a-zA-Z0-9]{20,}\\1',
            "AWS Key": r'(AKIA[0-9A-Z]{16})',
            "Generic Secret": r'(secret|password|token)[^a-zA-Z0-9]+(["\'`])[a-zA-Z0-9]{10,}\\2',
            "Private Key": r'-----BEGIN [A-Z ]+ PRIVATE KEY-----',
            "Connection String": r'(mongodb|postgresql|mysql|redis)://[a-zA-Z0-9]+:[a-zA-Z0-9]+@',
        }
        
        try:
            with open(os.path.join(self.repo_path, file_path), 'r') as f:
                content = f.readlines()
                
                for line_number, line in enumerate(content, 1):
                    for pattern_name, pattern in secret_patterns.items():
                        if re.search(pattern, line):
                            secrets.append({
                                "file": file_path,
                                "line": line_number,
                                "type": pattern_name,
                                "severity": "HIGH",
                                "recommendation": "Remove hardcoded secrets and use environment variables instead"
                            })
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
        
        return secrets
    
    def scan_for_vulnerabilities(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Scan a file for security vulnerabilities
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            List of detected vulnerabilities with line numbers and details
        """
        vulnerabilities = []
        
        # Vulnerability patterns to check for
        vulnerability_patterns = {
            "SQL Injection": {
                "pattern": r'exec(?:ute)?(?:_sql|_query)?\s*\(\s*["\']?\s*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)',
                "severity": "HIGH",
                "recommendation": "Use parameterized queries or an ORM instead of string concatenation"
            },
            "Command Injection": {
                "pattern": r'(?:os\.system|subprocess\.(?:call|run|Popen)|popen|exec)\s*\(\s*["\']?.*\$',
                "severity": "HIGH",
                "recommendation": "Use safe APIs and validate user input before passing to OS commands"
            },
            "XSS": {
                "pattern": r'(?:innerHTML|outerHTML|document\.write|eval)\s*\(\s*(?:[^)]*\$|.*\+\s*.*)',
                "severity": "MEDIUM",
                "recommendation": "Use content security policy and sanitize user input"
            },
            "Path Traversal": {
                "pattern": r'(?:open|read|write|file_get_contents)\s*\(\s*["\']?.*\.\./',
                "severity": "MEDIUM",
                "recommendation": "Validate and sanitize file paths, use path normalization"
            },
            "Insecure Cookie": {
                "pattern": r'(?:set_cookie|cookie)\s*\(\s*[^)]*(?:secure\s*=\s*false|httponly\s*=\s*false)',
                "severity": "LOW",
                "recommendation": "Set secure and httpOnly flags on cookies"
            }
        }
        
        try:
            with open(os.path.join(self.repo_path, file_path), 'r') as f:
                content = f.readlines()
                
                for line_number, line in enumerate(content, 1):
                    for vuln_name, vuln_info in vulnerability_patterns.items():
                        if re.search(vuln_info["pattern"], line):
                            vulnerabilities.append({
                                "file": file_path,
                                "line": line_number,
                                "type": vuln_name,
                                "severity": vuln_info["severity"],
                                "recommendation": vuln_info["recommendation"]
                            })
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
        
        return vulnerabilities
    
    def scan_dependencies(self) -> List[Dict[str, Any]]:
        """
        Scan project dependencies for known vulnerabilities
        
        Returns:
            List of vulnerable dependencies with CVE IDs and severity
        """
        vulnerabilities = []
        
        # Check if requirements.txt exists
        req_file = os.path.join(self.repo_path, "requirements.txt")
        if os.path.exists(req_file):
            # This is a simplified mock implementation
            # In a real implementation, you would use a tool like safety or pip-audit
            with open(req_file, 'r') as f:
                packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
                # Mock vulnerability database
                # In a real implementation, you would query a vulnerability database
                mock_vuln_db = {
                    "django<3.2.14": {
                        "cve": "CVE-2022-36359",
                        "severity": "MEDIUM",
                        "description": "Potential reflected file download vulnerability",
                        "recommendation": "Upgrade to Django 3.2.14 or newer"
                    },
                    "flask<2.0.0": {
                        "cve": "CVE-2021-28091",
                        "severity": "MEDIUM",
                        "description": "Flask Cookie deserialization issue",
                        "recommendation": "Upgrade to Flask 2.0.0 or newer"
                    },
                    "requests<2.26.0": {
                        "cve": "CVE-2021-33503",
                        "severity": "LOW",
                        "description": "CRLF injection vulnerability",
                        "recommendation": "Upgrade to requests 2.26.0 or newer"
                    }
                }
                
                for package in packages:
                    for vuln_pattern, vuln_info in mock_vuln_db.items():
                        package_name = package.split('==')[0] if '==' in package else package.split('>=')[0] if '>=' in package else package
                        if package_name in vuln_pattern:
                            vulnerabilities.append({
                                "package": package,
                                "cve": vuln_info["cve"],
                                "severity": vuln_info["severity"],
                                "description": vuln_info["description"],
                                "recommendation": vuln_info["recommendation"]
                            })
        
        return vulnerabilities
    
    def generate_report(self, output_file: str = "security_report.json") -> Dict[str, Any]:
        """
        Generate a comprehensive security report
        
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
        all_secrets = []
        all_vulnerabilities = []
        
        for file_path in python_files:
            secrets = self.scan_for_secrets(file_path)
            vulnerabilities = self.scan_for_vulnerabilities(file_path)
            
            all_secrets.extend(secrets)
            all_vulnerabilities.extend(vulnerabilities)
        
        # Scan dependencies
        dependency_vulnerabilities = self.scan_dependencies()
        
        # Compile report
        report = {
            "scan_date": datetime.now().isoformat(),
            "repository": self.repo_path,
            "summary": {
                "secret_count": len(all_secrets),
                "vulnerability_count": len(all_vulnerabilities),
                "dependency_vulnerability_count": len(dependency_vulnerabilities),
                "total_issues": len(all_secrets) + len(all_vulnerabilities) + len(dependency_vulnerabilities)
            },
            "secrets": all_secrets,
            "vulnerabilities": all_vulnerabilities,
            "dependency_vulnerabilities": dependency_vulnerabilities
        }
        
        # Write report to file
        with open(os.path.join(self.repo_path, output_file), 'w') as f:
            json.dump(report, f, indent=2)
        
        return report