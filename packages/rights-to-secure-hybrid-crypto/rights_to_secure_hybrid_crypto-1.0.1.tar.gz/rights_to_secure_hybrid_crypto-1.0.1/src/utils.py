"""
RightsToSecure Hybrid Crypto Wrapper - Utilities
Shared utilities for key generation, hashing, and KDF operations.
"""

import base64
import hashlib
import secrets
from typing import Tuple, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# Try to import OQS, fall back to mock if not available
try:
    import oqs
    OQS_AVAILABLE = True
except ImportError:
    try:
        import mock_oqs as oqs
        OQS_AVAILABLE = False
        print("⚠️  Using mock OQS implementation for testing")
    except ImportError:
        print("❌ Neither OQS nor mock OQS available")
        OQS_AVAILABLE = False


def generate_rsa_keys(key_size: int = 2048) -> Tuple[bytes, bytes]:
    """
    Generate RSA key pair.
    
    Args:
        key_size: RSA key size in bits (default: 2048)
        
    Returns:
        Tuple of (public_key_bytes, private_key_bytes) in PEM format
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )
    public_key = private_key.public_key()
    
    # Serialize keys to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    return public_pem, private_pem


def generate_ecdsa_keys(curve: str = "secp256r1") -> Tuple[bytes, bytes]:
    """
    Generate ECDSA key pair.
    
    Args:
        curve: Elliptic curve name (default: secp256r1)
        
    Returns:
        Tuple of (public_key_bytes, private_key_bytes) in PEM format
    """
    # Map curve names to cryptography curve objects
    curve_map = {
        "secp256r1": ec.SECP256R1(),
        "secp384r1": ec.SECP384R1(),
        "secp521r1": ec.SECP521R1(),
    }
    
    if curve not in curve_map:
        raise ValueError(f"Unsupported curve: {curve}")
    
    private_key = ec.generate_private_key(curve_map[curve])
    public_key = private_key.public_key()
    
    # Serialize keys to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    return public_pem, private_pem


def generate_kyber_keys(security_level: str = "Kyber512") -> Tuple[bytes, bytes]:
    """
    Generate Kyber key pair.
    
    Args:
        security_level: Kyber security level (Kyber512, Kyber768, Kyber1024)
        
    Returns:
        Tuple of (public_key_bytes, private_key_bytes)
    """
    if not OQS_AVAILABLE:
        print("⚠️  Using mock Kyber key generation")
    
    with oqs.KeyEncapsulation(security_level) as kem:
        public_key = kem.generate_keypair()
        private_key = kem.export_secret_key()
        
    return public_key, private_key


def generate_dilithium_keys(security_level: str = "Dilithium2") -> Tuple[bytes, bytes]:
    """
    Generate Dilithium key pair.
    
    Args:
        security_level: Dilithium security level (Dilithium2, Dilithium3, Dilithium5)
        
    Returns:
        Tuple of (public_key_bytes, private_key_bytes)
    """
    if not OQS_AVAILABLE:
        print("⚠️  Using mock Dilithium key generation")
    
    with oqs.Signature(security_level) as sig:
        public_key = sig.generate_keypair()
        private_key = sig.export_secret_key()
        
    return public_key, private_key


def shake256_hash(data: bytes, output_length: int = 32) -> bytes:
    """
    Generate SHAKE256 hash of data.
    
    Args:
        data: Input data to hash
        output_length: Length of output hash in bytes (default: 32)
        
    Returns:
        SHAKE256 hash as bytes
    """
    return hashlib.shake_256(data).digest(output_length)


def hkdf_derive_key(secret: bytes, salt: Optional[bytes] = None, 
                   info: Optional[bytes] = None, length: int = 32) -> bytes:
    """
    Derive a key using HKDF.
    
    Args:
        secret: Input secret material
        salt: Optional salt (if None, uses zero salt)
        info: Optional context information
        length: Output key length in bytes
        
    Returns:
        Derived key as bytes
    """
    if salt is None:
        salt = b'\x00' * 32
    
    if info is None:
        info = b'RightsToSecure-Hybrid-Crypto'
    
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        info=info,
    )
    
    return hkdf.derive(secret)


def encode_base64(data: bytes) -> str:
    """
    Encode bytes to base64 string.
    
    Args:
        data: Bytes to encode
        
    Returns:
        Base64 encoded string
    """
    return base64.b64encode(data).decode('utf-8')


def decode_base64(data: str) -> bytes:
    """
    Decode base64 string to bytes.
    
    Args:
        data: Base64 encoded string
        
    Returns:
        Decoded bytes
    """
    return base64.b64decode(data.encode('utf-8'))


def generate_random_bytes(length: int = 32) -> bytes:
    """
    Generate cryptographically secure random bytes.
    
    Args:
        length: Number of bytes to generate
        
    Returns:
        Random bytes
    """
    return secrets.token_bytes(length)


def combine_secrets(secret1: bytes, secret2: bytes) -> bytes:
    """
    Combine two secrets by concatenation.
    
    Args:
        secret1: First secret
        secret2: Second secret
        
    Returns:
        Combined secret
    """
    return secret1 + secret2


def split_hybrid_signature(hybrid_signature: bytes, 
                          classical_sig_length: int) -> Tuple[bytes, bytes]:
    """
    Split hybrid signature into classical and PQC components.
    
    Args:
        hybrid_signature: Combined hybrid signature
        classical_sig_length: Length of classical signature component
        
    Returns:
        Tuple of (classical_signature, pqc_signature)
    """
    if len(hybrid_signature) < classical_sig_length:
        raise ValueError("Hybrid signature too short")
    
    classical_sig = hybrid_signature[:classical_sig_length]
    pqc_sig = hybrid_signature[classical_sig_length:]
    
    return classical_sig, pqc_sig 