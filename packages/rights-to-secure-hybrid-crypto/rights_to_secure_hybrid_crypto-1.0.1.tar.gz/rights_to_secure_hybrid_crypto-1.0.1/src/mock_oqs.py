"""
Mock OQS module for testing purposes
This provides mock implementations when the real OQS library is not available
"""

import secrets
import hashlib
from typing import Tuple

class MockKeyEncapsulation:
    """Mock KeyEncapsulation class."""
    
    def __init__(self, algorithm: str):
        self.algorithm = algorithm
        self._public_key = None
        self._private_key = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass
    
    def generate_keypair(self) -> bytes:
        """Generate a mock keypair."""
        self._private_key = secrets.token_bytes(32)
        self._public_key = secrets.token_bytes(32)
        return self._public_key
    
    def export_secret_key(self) -> bytes:
        """Export the secret key."""
        if self._private_key is None:
            raise ValueError("No keypair generated")
        return self._private_key
    
    def import_secret_key(self, secret_key: bytes):
        """Import a secret key."""
        self._private_key = secret_key
    
    def encap_secret(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """Encapsulate a secret."""
        # For mock purposes, generate a deterministic shared secret
        # In real implementation, this would use the public key to encapsulate
        ciphertext = hashlib.sha256(public_key + b"ciphertext").digest()
        shared_secret = hashlib.sha256(public_key + b"shared_secret").digest()
        return ciphertext, shared_secret
    
    def decap_secret(self, ciphertext: bytes) -> bytes:
        """Decapsulate a secret."""
        if self._private_key is None:
            raise ValueError("No secret key imported")
        # Return a deterministic shared secret based on private key and ciphertext
        return hashlib.sha256(self._private_key + ciphertext).digest()

class MockSignature:
    """Mock Signature class."""
    
    def __init__(self, algorithm: str):
        self.algorithm = algorithm
        self._public_key = None
        self._private_key = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass
    
    def generate_keypair(self) -> bytes:
        """Generate a mock keypair."""
        self._private_key = secrets.token_bytes(32)
        self._public_key = secrets.token_bytes(32)
        return self._public_key
    
    def export_secret_key(self) -> bytes:
        """Export the secret key."""
        if self._private_key is None:
            raise ValueError("No keypair generated")
        return self._private_key
    
    def import_secret_key(self, secret_key: bytes):
        """Import a secret key."""
        self._private_key = secret_key
    
    def sign(self, message: bytes) -> bytes:
        """Sign a message."""
        if self._private_key is None:
            raise ValueError("No secret key imported")
        # Create a deterministic signature based on private key and message
        return hashlib.sha256(self._private_key + message).digest()
    
    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verify a signature."""
        # For mock purposes, verify by recreating the signature
        expected_signature = hashlib.sha256(public_key + message).digest()
        return signature == expected_signature

def KeyEncapsulation(algorithm: str):
    """Mock KeyEncapsulation function."""
    return MockKeyEncapsulation(algorithm)

def Signature(algorithm: str):
    """Mock Signature function."""
    return MockSignature(algorithm) 