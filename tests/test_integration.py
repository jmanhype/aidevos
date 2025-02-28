"""
AIDevOS Integration Tests
This module contains integration tests for the AIDevOS system.
"""

import unittest
import os
import sys
import json
import tempfile
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.integration.code_review import CodeReviewer
from src.integration.release_manager import ReleaseManager
from src.integration.branch_manager import BranchManager


class TestCodeReviewer(unittest.TestCase):
    """Tests for the code review module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        
        # Create a test file with code style issues
        self.test_file = os.path.join(self.test_dir.name, "test_style.py")
        with open(self.test_file, 'w') as f:
            f.write('"""\nTest file with style issues\n"""\n\n')
            f.write('def function_without_docstring():\n')
            f.write('    # This function has no docstring\n')
            f.write('    return "This function is too short to have style issues"\n\n')
            f.write('# A very long line that exceeds the 100 character limit by including many unnecessary words and characters to trigger the line length check\n\n')
            f.write('def another_function(param1, param2=[], param3={}):\n')  # Mutable default arguments
            f.write('    """This function has a docstring."""\n')
            f.write('    try:\n')
            f.write('        return param1 + param2\n')
            f.write('    except:\n')  # Bare except
            f.write('        return None\n')
        
        # Initialize code reviewer
        self.reviewer = CodeReviewer(self.test_dir.name)
    
    def tearDown(self):
        """Clean up after tests"""
        # Clean up temporary directory
        self.test_dir.cleanup()
    
    def test_check_code_style(self):
        """Test checking code style"""
        # Check style of the test file
        issues = self.reviewer.check_code_style(os.path.basename(self.test_file))
        
        # Verify that style issues were found
        self.assertGreaterEqual(len(issues), 1)
        
        # Check for specific style issues
        issue_types = [issue["type"] for issue in issues]
        self.assertIn("Missing Docstring", issue_types)
    
    def test_check_for_anti_patterns(self):
        """Test checking for anti-patterns"""
        # Check for anti-patterns in the test file
        issues = self.reviewer.check_for_anti_patterns(os.path.basename(self.test_file))
        
        # Verify that anti-patterns were found
        self.assertGreaterEqual(len(issues), 1)
        
        # Check for specific anti-patterns
        issue_types = [issue["type"] for issue in issues]
        self.assertIn("Bare Except", issue_types)
        self.assertIn("Mutable Default Argument", issue_types)
    
    def test_generate_review_report(self):
        """Test generating a review report"""
        # Generate a report
        report = self.reviewer.generate_review_report()
        
        # Verify report structure
        self.assertIn("summary", report)
        self.assertIn("style_issues", report)
        self.assertIn("complexity_issues", report)
        self.assertIn("anti_pattern_issues", report)


class TestReleaseManager(unittest.TestCase):
    """Tests for the release manager module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        
        # Initialize release manager
        self.manager = ReleaseManager(self.test_dir.name)
    
    def tearDown(self):
        """Clean up after tests"""
        # Clean up temporary directory
        self.test_dir.cleanup()
    
    def test_version_management(self):
        """Test version management functionality"""
        # Get the initial version
        initial_version = self.manager.get_current_version()
        self.assertEqual(initial_version, "0.1.0")  # Default initial version
        
        # Increment version numbers
        new_patch = self.manager.increment_version(initial_version, "patch")
        self.assertEqual(new_patch, "0.1.1")
        
        new_minor = self.manager.increment_version(initial_version, "minor")
        self.assertEqual(new_minor, "0.2.0")
        
        new_major = self.manager.increment_version(initial_version, "major")
        self.assertEqual(new_major, "1.0.0")
    
    def test_create_release(self):
        """Test creating a release"""
        # Create a change list
        changes = [
            {
                "type": "Feature",
                "description": "Added new feature X",
                "details": ["Implemented functionality Y", "Added tests"]
            },
            {
                "type": "Bugfix",
                "description": "Fixed issue Z",
                "details": ["Added null check", "Updated documentation"]
            }
        ]
        
        # Create a release
        release_info = self.manager.create_release(increment_type="minor", changes=changes)
        
        # Check release info
        self.assertEqual(release_info["version"], "0.2.0")
        self.assertIn("date", release_info)
        self.assertIn("release_notes_path", release_info)
        
        # Check that files were created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir.name, "VERSION")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir.name, "release_history.json")))
        self.assertTrue(os.path.exists(release_info["release_notes_path"]))
        
        # Check the content of the VERSION file
        with open(os.path.join(self.test_dir.name, "VERSION"), 'r') as f:
            version = f.read().strip()
            self.assertEqual(version, "0.2.0")


class TestBranchManager(unittest.TestCase):
    """Tests for the branch manager module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        
        # Initialize branch manager
        self.manager = BranchManager(self.test_dir.name)
    
    def tearDown(self):
        """Clean up after tests"""
        # Clean up temporary directory
        self.test_dir.cleanup()
    
    def test_branch_operations(self):
        """Test branch operations"""
        # Create a branch
        self.assertTrue(self.manager.create_branch("feature/test"))
        
        # Create a branch based on another
        self.assertTrue(self.manager.create_branch("feature/test2", "feature/test"))
        
        # Check conflicts
        conflicts = self.manager.check_conflicts("feature/test", "main")
        self.assertEqual(len(conflicts), 0)  # No conflicts in mock
        
        # Merge branches
        success, message = self.manager.merge_branch("feature/test", "main")
        self.assertTrue(success)
        self.assertIn("Successfully merged", message)
        
        # Delete a branch
        self.assertTrue(self.manager.delete_branch("feature/test"))
    
    def test_integrate_branches(self):
        """Test integrating all branches"""
        # Integrate branches
        result = self.manager.integrate_branches()
        
        # Check result
        self.assertIn("successful_merges", result)
        self.assertIn("failed_merges", result)
        self.assertIn("overall_success", result)


if __name__ == '__main__':
    unittest.main()