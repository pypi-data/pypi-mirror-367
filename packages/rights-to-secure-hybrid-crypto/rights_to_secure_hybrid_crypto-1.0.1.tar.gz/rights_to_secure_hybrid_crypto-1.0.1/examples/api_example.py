#!/usr/bin/env python3
"""
RightsToSecure Hybrid Crypto Wrapper - FastAPI Example
Demonstrates how to use the library as a REST API service.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from hybrid_kem import (
    hybrid_key_exchange,
    hybrid_key_decrypt,
    create_hybrid_key_exchange_package
)
from hybrid_signature import (
    hybrid_sign,
    hybrid_verify,
    get_signature_info
)
from utils import (
    generate_rsa_keys,
    generate_ecdsa_keys,
    generate_kyber_keys,
    generate_dilithium_keys,
    encode_base64,
    decode_base64
)

# Create FastAPI app
app = FastAPI(
    title="RightsToSecure Hybrid Crypto API",
    description="Quantum-resistant hybrid cryptography API combining classical and post-quantum algorithms",
    version="1.0.0",
    contact={
        "name": "Praveen Naidu",
        "email": "contact@arkaenterprises.com",
        "url": "https://rightstosecure.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Pydantic models for request/response
class KeyExchangeRequest(BaseModel):
    classical_type: str = "RSA"  # "RSA" or "ECC"
    rsa_key_size: Optional[int] = 2048
    ecc_curve: Optional[str] = "secp256r1"
    kyber_level: Optional[str] = "Kyber512"

class KeyExchangeResponse(BaseModel):
    classical_ciphertext: str
    kyber_ciphertext: str
    session_key: str
    classical_type: str
    version: str
    algorithm: str

class KeyDecryptRequest(BaseModel):
    classical_private_key: str
    kyber_private_key: str
    classical_ciphertext: str
    kyber_ciphertext: str
    classical_type: str = "RSA"

class KeyDecryptResponse(BaseModel):
    session_key: str
    success: bool

class SignatureRequest(BaseModel):
    message: str
    ecdsa_curve: str = "secp256r1"
    dilithium_level: str = "Dilithium2"

class SignatureResponse(BaseModel):
    ecdsa_signature: str
    dilithium_signature: str
    message_hash: str
    version: str
    algorithm: str
    ecdsa_curve: str
    dilithium_level: str

class VerificationRequest(BaseModel):
    message: str
    signature: Dict[str, Any]
    ecdsa_public_key: str
    dilithium_public_key: str

class VerificationResponse(BaseModel):
    valid: bool
    message: str

# In-memory key storage (in production, use secure key management)
key_store = {}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "RightsToSecure Hybrid Crypto API",
        "version": "1.0.0",
        "description": "Quantum-resistant hybrid cryptography API",
        "author": "Praveen Naidu",
        "contact": "contact@arkaenterprises.com",
        "website": "https://rightstosecure.com",
        "features": [
            "RSA + Kyber hybrid key exchange",
            "ECC + Kyber hybrid key exchange", 
            "ECDSA + Dilithium hybrid signatures",
            "Quantum-resistant cryptography",
            "Classical compatibility"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "RightsToSecure Hybrid Crypto API"}

@app.post("/keys/generate", response_model=Dict[str, str])
async def generate_keys(request: KeyExchangeRequest):
    """Generate key pairs for hybrid cryptography."""
    try:
        # Generate classical keys
        if request.classical_type.upper() == "RSA":
            classical_pub, classical_priv = generate_rsa_keys(request.rsa_key_size)
        elif request.classical_type.upper() == "ECC":
            classical_pub, classical_priv = generate_ecdsa_keys(request.ecc_curve)
        else:
            raise HTTPException(status_code=400, detail="Invalid classical type")
        
        # Generate Kyber keys
        kyber_pub, kyber_priv = generate_kyber_keys(request.kyber_level)
        
        # Generate Dilithium keys for signatures
        dilithium_pub, dilithium_priv = generate_dilithium_keys(request.dilithium_level)
        
        # Store keys (in production, use secure storage)
        key_id = encode_base64(generate_random_bytes(16))
        key_store[key_id] = {
            "classical_public": classical_pub,
            "classical_private": classical_priv,
            "kyber_public": kyber_pub,
            "kyber_private": kyber_priv,
            "dilithium_public": dilithium_pub,
            "dilithium_private": dilithium_priv,
            "classical_type": request.classical_type
        }
        
        return {
            "key_id": key_id,
            "classical_public_key": encode_base64(classical_pub),
            "kyber_public_key": encode_base64(kyber_pub),
            "dilithium_public_key": encode_base64(dilithium_pub),
            "classical_type": request.classical_type,
            "kyber_level": request.kyber_level,
            "dilithium_level": request.dilithium_level
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Key generation failed: {str(e)}")

@app.post("/keys/exchange", response_model=KeyExchangeResponse)
async def perform_key_exchange(request: KeyExchangeRequest):
    """Perform hybrid key exchange."""
    try:
        # Generate keys for this exchange
        if request.classical_type.upper() == "RSA":
            classical_pub, _ = generate_rsa_keys(request.rsa_key_size)
        elif request.classical_type.upper() == "ECC":
            classical_pub, _ = generate_ecdsa_keys(request.ecc_curve)
        else:
            raise HTTPException(status_code=400, detail="Invalid classical type")
        
        kyber_pub, _ = generate_kyber_keys(request.kyber_level)
        
        # Perform hybrid key exchange
        package = create_hybrid_key_exchange_package(
            classical_pub, kyber_pub, request.classical_type
        )
        
        return KeyExchangeResponse(**package)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Key exchange failed: {str(e)}")

@app.post("/keys/decrypt", response_model=KeyDecryptResponse)
async def decrypt_session_key(request: KeyDecryptRequest):
    """Decrypt session key from hybrid key exchange."""
    try:
        # Decode keys from base64
        classical_priv = decode_base64(request.classical_private_key)
        kyber_priv = decode_base64(request.kyber_private_key)
        
        # Decrypt session key
        session_key = hybrid_key_decrypt(
            classical_priv,
            kyber_priv,
            request.classical_ciphertext,
            request.kyber_ciphertext,
            request.classical_type
        )
        
        return KeyDecryptResponse(
            session_key=encode_base64(session_key),
            success=True
        )
        
    except Exception as e:
        return KeyDecryptResponse(
            session_key="",
            success=False
        )

@app.post("/sign", response_model=SignatureResponse)
async def create_signature(request: SignatureRequest):
    """Create hybrid digital signature."""
    try:
        # Generate keys for signing
        ecdsa_pub, ecdsa_priv = generate_ecdsa_keys(request.ecdsa_curve)
        dilithium_pub, dilithium_priv = generate_dilithium_keys(request.dilithium_level)
        
        # Create hybrid signature
        signature = hybrid_sign(
            request.message,
            ecdsa_priv,
            dilithium_priv,
            request.ecdsa_curve
        )
        
        return SignatureResponse(**signature)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signature creation failed: {str(e)}")

@app.post("/verify", response_model=VerificationResponse)
async def verify_signature(request: VerificationRequest):
    """Verify hybrid digital signature."""
    try:
        # Decode public keys from base64
        ecdsa_pub = decode_base64(request.ecdsa_public_key)
        dilithium_pub = decode_base64(request.dilithium_public_key)
        
        # Verify signature
        is_valid = hybrid_verify(
            request.message,
            request.signature,
            ecdsa_pub,
            dilithium_pub
        )
        
        return VerificationResponse(
            valid=is_valid,
            message="Signature verification completed"
        )
        
    except Exception as e:
        return VerificationResponse(
            valid=False,
            message=f"Verification failed: {str(e)}"
        )

@app.get("/signature/info")
async def get_signature_information(signature: str):
    """Get information about a hybrid signature."""
    try:
        # Parse signature from JSON string
        import json
        sig_data = json.loads(signature)
        
        # Extract information
        info = get_signature_info(sig_data)
        
        return {
            "signature_info": info,
            "signature_data": sig_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature format: {str(e)}")

@app.get("/algorithms")
async def get_supported_algorithms():
    """Get list of supported algorithms."""
    return {
        "classical_algorithms": {
            "rsa": {
                "key_sizes": [1024, 2048, 4096],
                "description": "Rivest-Shamir-Adleman asymmetric encryption"
            },
            "ecc": {
                "curves": ["secp256r1", "secp384r1", "secp521r1"],
                "description": "Elliptic Curve Cryptography"
            },
            "ecdsa": {
                "curves": ["secp256r1", "secp384r1", "secp521r1"],
                "description": "Elliptic Curve Digital Signature Algorithm"
            }
        },
        "post_quantum_algorithms": {
            "kyber": {
                "levels": ["Kyber512", "Kyber768", "Kyber1024"],
                "description": "Post-quantum key encapsulation mechanism"
            },
            "dilithium": {
                "levels": ["Dilithium2", "Dilithium3", "Dilithium5"],
                "description": "Post-quantum digital signature algorithm"
            }
        },
        "hybrid_combinations": {
            "key_exchange": ["RSA + Kyber", "ECC + Kyber"],
            "signatures": ["ECDSA + Dilithium"]
        }
    }

if __name__ == "__main__":
    print("🚀 Starting RightsToSecure Hybrid Crypto API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔗 Alternative docs: http://localhost:8000/redoc")
    print("🏥 Health check: http://localhost:8000/health")
    print()
    
    uvicorn.run(
        "api_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 