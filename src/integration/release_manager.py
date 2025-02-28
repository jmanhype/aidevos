"""
AIDevOS Release Manager
This module manages the release process for the AIDevOS system.
"""

import os
import re
import json
import subprocess
import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class ReleaseManager:
    """Manages releases for the AIDevOS system"""
    
    def __init__(self, repo_path: str):
        """
        Initialize the release manager
        
        Args:
            repo_path: Path to the code repository
        """
        self.repo_path = repo_path
        self.release_history_file = os.path.join(repo_path, "release_history.json")
    
    def get_current_version(self) -> str:
        """
        Get the current version of the system
        
        Returns:
            Current version string
        """
        # Check if version file exists
        version_file = os.path.join(self.repo_path, "VERSION")
        
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                return f.read().strip()
        
        # Fallback to release history
        if os.path.exists(self.release_history_file):
            with open(self.release_history_file, 'r') as f:
                history = json.load(f)
                if history["releases"]:
                    return history["releases"][0]["version"]
        
        # Default to initial version
        return "0.1.0"
    
    def increment_version(self, current_version: str, increment_type: str = "patch") -> str:
        """
        Increment the version number
        
        Args:
            current_version: Current version string
            increment_type: Type of increment (major, minor, patch)
            
        Returns:
            New version string
        """
        major, minor, patch = map(int, current_version.split('.'))
        
        if increment_type == "major":
            return f"{major + 1}.0.0"
        elif increment_type == "minor":
            return f"{major}.{minor + 1}.0"
        else:  # patch
            return f"{major}.{minor}.{patch + 1}"
    
    def create_release_notes(self, version: str, changes: List[Dict[str, Any]]) -> str:
        """
        Create release notes from changes
        
        Args:
            version: Version for this release
            changes: List of changes for this release
            
        Returns:
            Release notes as a string
        """
        release_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Group changes by type
        changes_by_type = {}
        for change in changes:
            change_type = change.get("type", "Other")
            if change_type not in changes_by_type:
                changes_by_type[change_type] = []
            changes_by_type[change_type].append(change)
        
        # Build release notes
        release_notes = [
            f"# Release {version} ({release_date})",
            "",
            "## Overview",
            "",
            "This release includes the following changes:",
            ""
        ]
        
        # Add changes by type
        for change_type, type_changes in changes_by_type.items():
            release_notes.append(f"### {change_type}")
            release_notes.append("")
            
            for change in type_changes:
                release_notes.append(f"- {change['description']}")
                
                # Add details if available
                if "details" in change:
                    for detail in change["details"]:
                        release_notes.append(f"  - {detail}")
            
            release_notes.append("")
        
        # Add footer
        release_notes.append("## Installation")
        release_notes.append("")
        release_notes.append("```bash")
        release_notes.append("pip install -r requirements.txt")
        release_notes.append("```")
        release_notes.append("")
        
        return "\n".join(release_notes)
    
    def update_release_history(self, version: str, changes: List[Dict[str, Any]]) -> None:
        """
        Update the release history file
        
        Args:
            version: Version for this release
            changes: List of changes for this release
        """
        release_date = datetime.datetime.now().isoformat()
        
        # Create new release entry
        new_release = {
            "version": version,
            "date": release_date,
            "changes": changes
        }
        
        # Load existing history or create new
        if os.path.exists(self.release_history_file):
            with open(self.release_history_file, 'r') as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = {"releases": []}
        else:
            history = {"releases": []}
        
        # Add new release to history
        history["releases"].insert(0, new_release)
        
        # Write updated history
        with open(self.release_history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def create_release(self, increment_type: str = "patch", changes: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new release
        
        Args:
            increment_type: Type of increment (major, minor, patch)
            changes: List of changes for this release
            
        Returns:
            Release information
        """
        # Get current version and increment
        current_version = self.get_current_version()
        new_version = self.increment_version(current_version, increment_type)
        
        # Default changes if not provided
        if changes is None:
            changes = []
        
        # Create release notes
        release_notes = self.create_release_notes(new_version, changes)
        
        # Write release notes to file
        release_notes_path = os.path.join(self.repo_path, f"RELEASE_NOTES_{new_version}.md")
        with open(release_notes_path, 'w') as f:
            f.write(release_notes)
        
        # Update version file
        version_file = os.path.join(self.repo_path, "VERSION")
        with open(version_file, 'w') as f:
            f.write(new_version)
        
        # Update release history
        self.update_release_history(new_version, changes)
        
        # Return release info
        return {
            "version": new_version,
            "date": datetime.datetime.now().isoformat(),
            "release_notes_path": release_notes_path,
            "changes": changes
        }
    
    def validate_release(self, version: str) -> Dict[str, Any]:
        """
        Validate a release before deployment
        
        Args:
            version: Version to validate
            
        Returns:
            Validation results
        """
        results = {
            "version": version,
            "validation_date": datetime.datetime.now().isoformat(),
            "checks": [],
            "passed": True
        }
        
        # Check 1: Ensure all tests pass
        test_results = self._run_tests()
        results["checks"].append({
            "name": "Unit Tests",
            "passed": test_results["passed"],
            "details": test_results["details"]
        })
        
        if not test_results["passed"]:
            results["passed"] = False
        
        # Check 2: Ensure documentation is up to date
        doc_results = self._check_documentation()
        results["checks"].append({
            "name": "Documentation",
            "passed": doc_results["passed"],
            "details": doc_results["details"]
        })
        
        if not doc_results["passed"]:
            results["passed"] = False
        
        # Check 3: Security scan
        security_results = self._run_security_scan()
        results["checks"].append({
            "name": "Security Scan",
            "passed": security_results["passed"],
            "details": security_results["details"]
        })
        
        if not security_results["passed"]:
            results["passed"] = False
        
        return results
    
    def _run_tests(self) -> Dict[str, Any]:
        """
        Run tests for the system
        
        Returns:
            Test results
        """
        # This is a mock implementation
        # In a real implementation, you would run pytest or other test framework
        return {
            "passed": True,
            "details": "All tests passed"
        }
    
    def _check_documentation(self) -> Dict[str, Any]:
        """
        Check if documentation is up to date
        
        Returns:
            Documentation check results
        """
        # This is a mock implementation
        # In a real implementation, you would check for outdated docs
        docs_path = os.path.join(self.repo_path, "docs")
        if not os.path.exists(docs_path):
            return {
                "passed": False,
                "details": "Documentation directory not found"
            }
        
        return {
            "passed": True,
            "details": "Documentation is up to date"
        }
    
    def _run_security_scan(self) -> Dict[str, Any]:
        """
        Run a security scan on the codebase
        
        Returns:
            Security scan results
        """
        # This is a mock implementation
        # In a real implementation, you would use the VulnerabilityScanner
        return {
            "passed": True,
            "details": "No security issues found"
        }
    
    def create_release_branch(self, version: str) -> bool:
        """
        Create a release branch
        
        Args:
            version: Version for this release
            
        Returns:
            Success status
        """
        # This is a mock implementation
        # In a real implementation, you would use git commands
        release_branch = f"release-{version}"
        print(f"Created release branch: {release_branch}")
        return True
    
    def merge_branches(self, source_branch: str, target_branch: str) -> bool:
        """
        Merge a source branch into a target branch
        
        Args:
            source_branch: Source branch name
            target_branch: Target branch name
            
        Returns:
            Success status
        """
        # This is a mock implementation
        # In a real implementation, you would use git commands
        print(f"Merged {source_branch} into {target_branch}")
        return True