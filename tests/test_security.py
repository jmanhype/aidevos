"""
AIDevOS Security Tests
This module contains security tests for the AIDevOS system.
"""

import unittest
import os
import sys
import json
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.security.authentication import AuthenticationManager, AuthorizationManager
from src.security.encryption import EncryptionManager
from src.security.scanner import VulnerabilityScanner


class TestAuthentication(unittest.TestCase):
    """Tests for the authentication module"""
    
    def test_create_access_token(self):
        """Test creating and validating access tokens"""
        # Create a token
        user_data = {"sub": "user123", "roles": ["admin", "user"]}
        token = AuthenticationManager.create_access_token(user_data)
        
        # Verify it's a string
        self.assertIsInstance(token, str)
        
        # Verify the token
        payload = AuthenticationManager.verify_token(token)
        
        # Check payload content
        self.assertIsNotNone(payload)
        self.assertEqual(payload["sub"], "user123")
        self.assertListEqual(payload["roles"], ["admin", "user"])
    
    def test_invalid_token(self):
        """Test that invalid tokens are rejected"""
        # Create an invalid token
        invalid_token = "invalid.token.string"
        
        # Verify it fails
        payload = AuthenticationManager.verify_token(invalid_token)
        self.assertIsNone(payload)


class TestAuthorization(unittest.TestCase):
    """Tests for the authorization module"""
    
    def test_has_permission(self):
        """Test permission checking"""
        # User has a required role
        self.assertTrue(AuthorizationManager.has_permission(
            user_roles=["user", "editor"],
            required_roles=["admin", "editor"]
        ))
        
        # User doesn't have any required role
        self.assertFalse(AuthorizationManager.has_permission(
            user_roles=["user", "editor"],
            required_roles=["admin", "owner"]
        ))
        
        # Empty roles
        self.assertFalse(AuthorizationManager.has_permission(
            user_roles=[],
            required_roles=["admin", "user"]
        ))
        
        # Empty required roles (always true)
        self.assertFalse(AuthorizationManager.has_permission(
            user_roles=["user", "admin"],
            required_roles=[]
        ))


class TestEncryption(unittest.TestCase):
    """Tests for the encryption module"""
    
    def test_generate_key(self):
        """Test key generation"""
        key = EncryptionManager.generate_key("secure_password")
        self.assertIsInstance(key, bytes)
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption"""
        # Generate a key
        key = EncryptionManager.generate_key("secure_password")
        
        # Test data
        original_data = "This is sensitive data that needs encryption"
        
        # Encrypt data
        encrypted_data = EncryptionManager.encrypt_data(original_data, key)
        self.assertIsInstance(encrypted_data, bytes)
        
        # Decrypt data
        decrypted_data = EncryptionManager.decrypt_data(encrypted_data, key)
        self.assertEqual(decrypted_data, original_data)
    
    def test_different_keys(self):
        """Test that different keys produce different results"""
        # Generate two different keys
        key1 = EncryptionManager.generate_key("password1")
        key2 = EncryptionManager.generate_key("password2")
        
        # Test data
        original_data = "Sensitive data"
        
        # Encrypt with first key
        encrypted_data = EncryptionManager.encrypt_data(original_data, key1)
        
        # Attempt to decrypt with second key (should fail)
        with self.assertRaises(Exception):
            EncryptionManager.decrypt_data(encrypted_data, key2)


class TestSecurityScanner(unittest.TestCase):
    """Tests for the security scanner"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary test file with secrets
        self.test_dir = Path(os.path.dirname(__file__)) / "test_data"
        self.test_dir.mkdir(exist_ok=True)
        
        # Create a test file with a mock secret
        self.test_file = self.test_dir / "test_file.py"
        with open(self.test_file, 'w') as f:
            f.write('api_key = "api_key_abcdefghijklmnopqrstuvwxyz123456789"\n')
            f.write('# This is a harmless comment\n')
            f.write('password = "secure_password"\n')  # Not long enough to trigger
        
        # Initialize scanner
        self.scanner = VulnerabilityScanner(str(self.test_dir))
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove test files
        if self.test_file.exists():
            self.test_file.unlink()
        
        # Remove test directory
        if self.test_dir.exists():
            self.test_dir.rmdir()
    
    def test_scan_for_secrets(self):
        """Test scanning for secrets"""
        # Scan the test file
        secrets = self.scanner.scan_for_secrets(str(self.test_file.relative_to(self.test_dir)))
        
        # Check that the API key was found
        self.assertGreaterEqual(len(secrets), 1)
        
        # Check secret details
        found_api_key = False
        for secret in secrets:
            if "API Key" in secret["type"]:
                found_api_key = True
                break
        
        self.assertTrue(found_api_key)


if __name__ == '__main__':
    unittest.main()