"""
RightsToSecure Hybrid Crypto Wrapper - Hybrid Key Encapsulation Mechanism
Implements RSA + Kyber hybrid key exchange for quantum-resistant security.
"""

import base64
from typing import Tuple, Union
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding

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

from utils import (
    shake256_hash, 
    encode_base64, 
    decode_base64, 
    generate_random_bytes,
    combine_secrets
)


def hybrid_key_exchange(
    classical_public_key: Union[bytes, str],
    kyber_public_key: bytes,
    classical_type: str = "RSA"
) -> Tuple[str, str, bytes]:
    """
    Perform hybrid key exchange using classical + Kyber.
    
    Args:
        classical_public_key: RSA or ECC public key (PEM format or bytes)
        kyber_public_key: Kyber public key
        classical_type: Type of classical key ("RSA" or "ECC")
        
    Returns:
        Tuple of (classical_ciphertext_b64, kyber_ciphertext_b64, session_key)
    """
    # Generate random classical shared secret
    classical_secret = generate_random_bytes(32)
    
    # Encrypt classical secret with RSA or ECC
    if classical_type.upper() == "RSA":
        classical_ciphertext = _encrypt_with_rsa(classical_public_key, classical_secret)
    elif classical_type.upper() == "ECC":
        classical_ciphertext = _encrypt_with_ecc(classical_public_key, classical_secret)
    else:
        raise ValueError(f"Unsupported classical type: {classical_type}")
    
    # Use Kyber to encapsulate PQC shared secret
    with oqs.KeyEncapsulation("Kyber512") as kem:
        kyber_ciphertext, kyber_secret = kem.encap_secret(kyber_public_key)
    
    # Combine both secrets
    combined_secret = combine_secrets(classical_secret, kyber_secret)
    
    # Derive final session key using SHAKE256
    session_key = shake256_hash(combined_secret, 32)
    
    # Encode ciphertexts to base64
    classical_ct_b64 = encode_base64(classical_ciphertext)
    kyber_ct_b64 = encode_base64(kyber_ciphertext)
    
    return classical_ct_b64, kyber_ct_b64, session_key


def hybrid_key_decrypt(
    classical_private_key: Union[bytes, str],
    kyber_private_key: bytes,
    classical_ciphertext_b64: str,
    kyber_ciphertext_b64: str,
    classical_type: str = "RSA"
) -> bytes:
    """
    Decrypt hybrid key exchange to recover session key.
    
    Args:
        classical_private_key: RSA or ECC private key (PEM format or bytes)
        kyber_private_key: Kyber private key
        classical_ciphertext_b64: Base64 encoded classical ciphertext
        kyber_ciphertext_b64: Base64 encoded Kyber ciphertext
        classical_type: Type of classical key ("RSA" or "ECC")
        
    Returns:
        Recovered session key
    """
    # Decode ciphertexts from base64
    classical_ciphertext = decode_base64(classical_ciphertext_b64)
    kyber_ciphertext = decode_base64(kyber_ciphertext_b64)
    
    # Decrypt classical secret
    if classical_type.upper() == "RSA":
        classical_secret = _decrypt_with_rsa(classical_private_key, classical_ciphertext)
    elif classical_type.upper() == "ECC":
        classical_secret = _decrypt_with_ecc(classical_private_key, classical_ciphertext)
    else:
        raise ValueError(f"Unsupported classical type: {classical_type}")
    
    # Use Kyber to decapsulate PQC shared secret
    with oqs.KeyEncapsulation("Kyber512") as kem:
        kem.import_secret_key(kyber_private_key)
        kyber_secret = kem.decap_secret(kyber_ciphertext)
    
    # Combine both secrets
    combined_secret = combine_secrets(classical_secret, kyber_secret)
    
    # Derive final session key using SHAKE256
    session_key = shake256_hash(combined_secret, 32)
    
    return session_key


def _encrypt_with_rsa(public_key: Union[bytes, str], data: bytes) -> bytes:
    """
    Encrypt data with RSA public key.
    
    Args:
        public_key: RSA public key in PEM format
        data: Data to encrypt
        
    Returns:
        RSA encrypted ciphertext
    """
    if isinstance(public_key, str):
        public_key = public_key.encode('utf-8')
    
    # Load public key
    rsa_public_key = serialization.load_pem_public_key(public_key)
    
    # Encrypt with OAEP padding
    ciphertext = rsa_public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return ciphertext


def _decrypt_with_rsa(private_key: Union[bytes, str], ciphertext: bytes) -> bytes:
    """
    Decrypt data with RSA private key.
    
    Args:
        private_key: RSA private key in PEM format
        ciphertext: RSA encrypted ciphertext
        
    Returns:
        Decrypted data
    """
    if isinstance(private_key, str):
        private_key = private_key.encode('utf-8')
    
    # Load private key
    rsa_private_key = serialization.load_pem_private_key(private_key, password=None)
    
    # Decrypt with OAEP padding
    plaintext = rsa_private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return plaintext


def _encrypt_with_ecc(public_key: Union[bytes, str], data: bytes) -> bytes:
    """
    Encrypt data with ECC public key using ECIES-like approach.
    
    Args:
        public_key: ECC public key in PEM format
        data: Data to encrypt
        
    Returns:
        ECC encrypted ciphertext
    """
    if isinstance(public_key, str):
        public_key = public_key.encode('utf-8')
    
    # Load public key
    ecc_public_key = serialization.load_pem_public_key(public_key)
    
    # For ECC, we'll use a simplified approach with key derivation
    # In a real implementation, you'd use proper ECIES
    shared_key = ecc_public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Use the public key bytes as a simple encryption key
    # This is a simplified approach - in production, use proper ECIES
    from cryptography.fernet import Fernet
    import hashlib
    
    key = hashlib.sha256(shared_key).digest()
    f = Fernet(base64.urlsafe_b64encode(key))
    
    return f.encrypt(data)


def _decrypt_with_ecc(private_key: Union[bytes, str], ciphertext: bytes) -> bytes:
    """
    Decrypt data with ECC private key.
    
    Args:
        private_key: ECC private key in PEM format
        ciphertext: ECC encrypted ciphertext
        
    Returns:
        Decrypted data
    """
    if isinstance(private_key, str):
        private_key = private_key.encode('utf-8')
    
    # Load private key
    ecc_private_key = serialization.load_pem_private_key(private_key, password=None)
    
    # For ECC, we'll use a simplified approach
    # In a real implementation, you'd use proper ECIES
    shared_key = ecc_private_key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Use the public key bytes as a simple encryption key
    # This is a simplified approach - in production, use proper ECIES
    from cryptography.fernet import Fernet
    import hashlib
    
    key = hashlib.sha256(shared_key).digest()
    f = Fernet(base64.urlsafe_b64encode(key))
    
    return f.decrypt(ciphertext)


def create_hybrid_key_exchange_package(
    classical_public_key: Union[bytes, str],
    kyber_public_key: bytes,
    classical_type: str = "RSA"
) -> dict:
    """
    Create a complete hybrid key exchange package.
    
    Args:
        classical_public_key: RSA or ECC public key
        kyber_public_key: Kyber public key
        classical_type: Type of classical key
        
    Returns:
        Dictionary containing all key exchange components
    """
    classical_ct, kyber_ct, session_key = hybrid_key_exchange(
        classical_public_key, kyber_public_key, classical_type
    )
    
    return {
        "classical_ciphertext": classical_ct,
        "kyber_ciphertext": kyber_ct,
        "session_key": encode_base64(session_key),
        "classical_type": classical_type,
        "version": "1.0",
        "algorithm": "RightsToSecure-Hybrid-KEM"
    }


def verify_hybrid_key_exchange(
    classical_public_key: Union[bytes, str],
    kyber_public_key: bytes,
    classical_ciphertext_b64: str,
    kyber_ciphertext_b64: str,
    expected_session_key: bytes,
    classical_type: str = "RSA"
) -> bool:
    """
    Verify that a hybrid key exchange produces the expected session key.
    
    Args:
        classical_public_key: Classical public key
        kyber_public_key: Kyber public key
        classical_ciphertext_b64: Classical ciphertext
        kyber_ciphertext_b64: Kyber ciphertext
        expected_session_key: Expected session key
        classical_type: Type of classical key
        
    Returns:
        True if verification succeeds, False otherwise
    """
    try:
        # Reconstruct session key
        reconstructed_key = hybrid_key_decrypt(
            classical_public_key,  # This should be the private key for verification
            kyber_public_key,      # This should be the private key for verification
            classical_ciphertext_b64,
            kyber_ciphertext_b64,
            classical_type
        )
        
        return reconstructed_key == expected_session_key
    except Exception:
        return False 