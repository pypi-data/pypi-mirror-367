"""
RightsToSecure Hybrid Crypto Wrapper - Hybrid Digital Signatures
Implements ECDSA + Dilithium hybrid digital signatures for quantum-resistant security.
"""

import json
import base64
from typing import Union, Tuple, Dict, Any
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils

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
    encode_base64, 
    decode_base64, 
    split_hybrid_signature
)


def hybrid_sign(
    message: Union[bytes, str],
    ecdsa_private_key: Union[bytes, str],
    dilithium_private_key: bytes,
    ecdsa_curve: str = "secp256r1"
) -> Dict[str, Any]:
    """
    Create a hybrid digital signature using ECDSA + Dilithium.
    
    Args:
        message: Message to sign (bytes or string)
        ecdsa_private_key: ECDSA private key (PEM format or bytes)
        dilithium_private_key: Dilithium private key
        ecdsa_curve: ECDSA curve name (default: secp256r1)
        
    Returns:
        Dictionary containing hybrid signature components
    """
    # Convert message to bytes if it's a string
    if isinstance(message, str):
        message = message.encode('utf-8')
    
    # Sign with ECDSA
    ecdsa_signature = _sign_with_ecdsa(message, ecdsa_private_key, ecdsa_curve)
    
    # Sign with Dilithium
    with oqs.Signature("Dilithium2") as sig:
        sig.import_secret_key(dilithium_private_key)
        dilithium_signature = sig.sign(message)
    
    # Create hybrid signature structure
    hybrid_signature = {
        "ecdsa_signature": encode_base64(ecdsa_signature),
        "dilithium_signature": encode_base64(dilithium_signature),
        "message_hash": encode_base64(_hash_message(message)),
        "version": "1.0",
        "algorithm": "RightsToSecure-Hybrid-Signature",
        "ecdsa_curve": ecdsa_curve,
        "dilithium_level": "Dilithium2"
    }
    
    return hybrid_signature


def hybrid_verify(
    message: Union[bytes, str],
    hybrid_signature: Dict[str, Any],
    ecdsa_public_key: Union[bytes, str],
    dilithium_public_key: bytes
) -> bool:
    """
    Verify a hybrid digital signature.
    
    Args:
        message: Original message (bytes or string)
        hybrid_signature: Hybrid signature dictionary
        ecdsa_public_key: ECDSA public key (PEM format or bytes)
        dilithium_public_key: Dilithium public key
        
    Returns:
        True if both signatures are valid, False otherwise
    """
    # Convert message to bytes if it's a string
    if isinstance(message, str):
        message = message.encode('utf-8')
    
    try:
        # Extract signature components
        ecdsa_sig_b64 = hybrid_signature.get("ecdsa_signature")
        dilithium_sig_b64 = hybrid_signature.get("dilithium_signature")
        
        if not ecdsa_sig_b64 or not dilithium_sig_b64:
            return False
        
        ecdsa_signature = decode_base64(ecdsa_sig_b64)
        dilithium_signature = decode_base64(dilithium_sig_b64)
        
        # Verify ECDSA signature
        ecdsa_valid = _verify_ecdsa(message, ecdsa_signature, ecdsa_public_key)
        
        # Verify Dilithium signature
        with oqs.Signature("Dilithium2") as sig:
            dilithium_valid = sig.verify(message, dilithium_signature, dilithium_public_key)
        
        # Both signatures must be valid
        return ecdsa_valid and dilithium_valid
        
    except Exception:
        return False


def _sign_with_ecdsa(
    message: bytes, 
    private_key: Union[bytes, str], 
    curve: str = "secp256r1"
) -> bytes:
    """
    Sign message with ECDSA.
    
    Args:
        message: Message to sign
        private_key: ECDSA private key
        curve: ECDSA curve name
        
    Returns:
        ECDSA signature as bytes
    """
    if isinstance(private_key, str):
        private_key = private_key.encode('utf-8')
    
    # Load private key
    ecdsa_private_key = serialization.load_pem_private_key(private_key, password=None)
    
    # Choose hash algorithm based on curve
    hash_algorithm = _get_hash_for_curve(curve)
    
    # Sign the message
    signature = ecdsa_private_key.sign(
        message,
        ec.ECDSA(hash_algorithm)
    )
    
    return signature


def _verify_ecdsa(
    message: bytes, 
    signature: bytes, 
    public_key: Union[bytes, str]
) -> bool:
    """
    Verify ECDSA signature.
    
    Args:
        message: Original message
        signature: ECDSA signature
        public_key: ECDSA public key
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        if isinstance(public_key, str):
            public_key = public_key.encode('utf-8')
        
        # Load public key
        ecdsa_public_key = serialization.load_pem_public_key(public_key)
        
        # Verify signature (using SHA256 as default)
        ecdsa_public_key.verify(
            signature,
            message,
            ec.ECDSA(hashes.SHA256())
        )
        
        return True
    except Exception:
        return False


def _get_hash_for_curve(curve: str) -> hashes.HashAlgorithm:
    """
    Get appropriate hash algorithm for ECDSA curve.
    
    Args:
        curve: ECDSA curve name
        
    Returns:
        Hash algorithm object
    """
    curve_hash_map = {
        "secp256r1": hashes.SHA256(),
        "secp384r1": hashes.SHA384(),
        "secp521r1": hashes.SHA512(),
    }
    
    return curve_hash_map.get(curve, hashes.SHA256())


def _hash_message(message: bytes) -> bytes:
    """
    Hash message using SHA-256.
    
    Args:
        message: Message to hash
        
    Returns:
        Message hash
    """
    return hashes.Hash(hashes.SHA256()).finalize()


def create_compact_hybrid_signature(
    message: Union[bytes, str],
    ecdsa_private_key: Union[bytes, str],
    dilithium_private_key: bytes,
    ecdsa_curve: str = "secp256r1"
) -> str:
    """
    Create a compact hybrid signature (concatenated format).
    
    Args:
        message: Message to sign
        ecdsa_private_key: ECDSA private key
        dilithium_private_key: Dilithium private key
        ecdsa_curve: ECDSA curve name
        
    Returns:
        Base64 encoded compact hybrid signature
    """
    # Convert message to bytes if it's a string
    if isinstance(message, str):
        message = message.encode('utf-8')
    
    # Sign with ECDSA
    ecdsa_signature = _sign_with_ecdsa(message, ecdsa_private_key, ecdsa_curve)
    
    # Sign with Dilithium
    with oqs.Signature("Dilithium2") as sig:
        sig.import_secret_key(dilithium_private_key)
        dilithium_signature = sig.sign(message)
    
    # Concatenate signatures
    hybrid_signature = ecdsa_signature + dilithium_signature
    
    # Encode to base64
    return encode_base64(hybrid_signature)


def verify_compact_hybrid_signature(
    message: Union[bytes, str],
    compact_signature: str,
    ecdsa_public_key: Union[bytes, str],
    dilithium_public_key: bytes,
    ecdsa_signature_length: int = 64  # Default for secp256r1
) -> bool:
    """
    Verify a compact hybrid signature.
    
    Args:
        message: Original message
        compact_signature: Base64 encoded compact hybrid signature
        ecdsa_public_key: ECDSA public key
        dilithium_public_key: Dilithium public key
        ecdsa_signature_length: Length of ECDSA signature component
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Convert message to bytes if it's a string
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Decode compact signature
        hybrid_signature = decode_base64(compact_signature)
        
        # Split into components
        ecdsa_signature, dilithium_signature = split_hybrid_signature(
            hybrid_signature, ecdsa_signature_length
        )
        
        # Verify ECDSA signature
        ecdsa_valid = _verify_ecdsa(message, ecdsa_signature, ecdsa_public_key)
        
        # Verify Dilithium signature
        with oqs.Signature("Dilithium2") as sig:
            dilithium_valid = sig.verify(message, dilithium_signature, dilithium_public_key)
        
        # Both signatures must be valid
        return ecdsa_valid and dilithium_valid
        
    except Exception:
        return False


def get_signature_info(hybrid_signature: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract information from a hybrid signature.
    
    Args:
        hybrid_signature: Hybrid signature dictionary
        
    Returns:
        Dictionary containing signature information
    """
    return {
        "version": hybrid_signature.get("version"),
        "algorithm": hybrid_signature.get("algorithm"),
        "ecdsa_curve": hybrid_signature.get("ecdsa_curve"),
        "dilithium_level": hybrid_signature.get("dilithium_level"),
        "ecdsa_signature_length": len(decode_base64(hybrid_signature.get("ecdsa_signature", ""))),
        "dilithium_signature_length": len(decode_base64(hybrid_signature.get("dilithium_signature", ""))),
        "total_signature_length": len(decode_base64(hybrid_signature.get("ecdsa_signature", ""))) + 
                                len(decode_base64(hybrid_signature.get("dilithium_signature", "")))
    }


def export_signature_to_json(hybrid_signature: Dict[str, Any]) -> str:
    """
    Export hybrid signature to JSON string.
    
    Args:
        hybrid_signature: Hybrid signature dictionary
        
    Returns:
        JSON string representation
    """
    return json.dumps(hybrid_signature, indent=2)


def import_signature_from_json(json_string: str) -> Dict[str, Any]:
    """
    Import hybrid signature from JSON string.
    
    Args:
        json_string: JSON string representation
        
    Returns:
        Hybrid signature dictionary
    """
    return json.loads(json_string) 