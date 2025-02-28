"""
AIDevOS Encryption Module
This module handles data encryption and protection for the AIDevOS system.
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Encryption key used by Fernet
# In production, this should be loaded from a secure environment variable
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")


class EncryptionManager:
    """Manages data encryption and decryption for the AIDevOS system"""
    
    @staticmethod
    def generate_key(password: str, salt: bytes = None) -> bytes:
        """
        Generate an encryption key from a password using PBKDF2
        
        Args:
            password: Password to derive the key from
            salt: Optional salt for key derivation
            
        Returns:
            Encryption key
        """
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    @staticmethod
    def encrypt_data(data: str, key: bytes = None) -> bytes:
        """
        Encrypt data using Fernet symmetric encryption
        
        Args:
            data: Data to encrypt
            key: Optional encryption key (uses env var if not provided)
            
        Returns:
            Encrypted data
        """
        if key is None:
            if ENCRYPTION_KEY is None:
                raise ValueError("Encryption key not provided and not found in environment")
            key = ENCRYPTION_KEY.encode()
            
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        
        return encrypted_data
    
    @staticmethod
    def decrypt_data(encrypted_data: bytes, key: bytes = None) -> str:
        """
        Decrypt data using Fernet symmetric encryption
        
        Args:
            encrypted_data: Data to decrypt
            key: Optional encryption key (uses env var if not provided)
            
        Returns:
            Decrypted data as string
        """
        if key is None:
            if ENCRYPTION_KEY is None:
                raise ValueError("Encryption key not provided and not found in environment")
            key = ENCRYPTION_KEY.encode()
            
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data).decode()
        
        return decrypted_data