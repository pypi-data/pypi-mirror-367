# 🔐 RightsToSecure Hybrid Crypto Wrapper - Usage Guide

> **Complete guide to using the quantum-resistant hybrid cryptography library**

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [API Usage](#api-usage)
6. [Docker Deployment](#docker-deployment)
7. [Testing](#testing)
8. [Security Best Practices](#security-best-practices)
9. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for cloning)

### Installation

```bash
# Clone the repository
git clone https://github.com/rightstosecure/hybrid-crypto.git
cd hybrid-crypto

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Basic Example

```python
from src import hybrid_key_exchange, hybrid_key_decrypt, generate_rsa_keys, generate_kyber_keys

# Generate key pairs
rsa_pub, rsa_priv = generate_rsa_keys(2048)
kyber_pub, kyber_priv = generate_kyber_keys("Kyber512")

# Perform hybrid key exchange
rsa_ct, kyber_ct, session_key = hybrid_key_exchange(rsa_pub, kyber_pub, "RSA")

# Reconstruct session key
reconstructed_key = hybrid_key_decrypt(rsa_priv, kyber_priv, rsa_ct, kyber_ct, "RSA")

print("Session keys match:", session_key == reconstructed_key)
```

---

## 📦 Installation

### Method 1: From Source

```bash
git clone https://github.com/rightstosecure/hybrid-crypto.git
cd hybrid-crypto
pip install -r requirements.txt
pip install -e .
```

### Method 2: Using Docker

```bash
# Build the Docker image
docker build -t rights-to-secure-hybrid-crypto .

# Run the API
docker run -p 8000:8000 rights-to-secure-hybrid-crypto
```

### Method 3: Using Docker Compose

```bash
# Start the API service
docker-compose up hybrid-crypto-api

# Start development environment
docker-compose --profile dev up

# Run tests
docker-compose --profile test up
```

---

## 🔧 Basic Usage

### 1. Hybrid Key Exchange

#### RSA + Kyber

```python
from src import (
    hybrid_key_exchange, 
    hybrid_key_decrypt, 
    generate_rsa_keys, 
    generate_kyber_keys
)

# Generate key pairs
rsa_pub, rsa_priv = generate_rsa_keys(2048)
kyber_pub, kyber_priv = generate_kyber_keys("Kyber512")

# Sender: Perform key exchange
rsa_ciphertext, kyber_ciphertext, session_key = hybrid_key_exchange(
    rsa_pub, kyber_pub, "RSA"
)

# Receiver: Reconstruct session key
reconstructed_key = hybrid_key_decrypt(
    rsa_priv, kyber_priv, rsa_ciphertext, kyber_ciphertext, "RSA"
)

# Verify keys match
assert session_key == reconstructed_key
print(f"Session key: {session_key.hex()}")
```

#### ECC + Kyber

```python
from src import generate_ecdsa_keys

# Generate ECC keys instead of RSA
ecc_pub, ecc_priv = generate_ecdsa_keys("secp256r1")

# Perform ECC + Kyber key exchange
ecc_ciphertext, kyber_ciphertext, session_key = hybrid_key_exchange(
    ecc_pub, kyber_pub, "ECC"
)

# Reconstruct session key
reconstructed_key = hybrid_key_decrypt(
    ecc_priv, kyber_priv, ecc_ciphertext, kyber_ciphertext, "ECC"
)
```

### 2. Hybrid Digital Signatures

#### ECDSA + Dilithium

```python
from src import (
    hybrid_sign, 
    hybrid_verify, 
    generate_ecdsa_keys, 
    generate_dilithium_keys
)

# Generate key pairs
ecdsa_pub, ecdsa_priv = generate_ecdsa_keys("secp256r1")
dilithium_pub, dilithium_priv = generate_dilithium_keys("Dilithium2")

# Message to sign
message = "Confidential data for RightsToSecure"

# Create hybrid signature
signature = hybrid_sign(message, ecdsa_priv, dilithium_priv, "secp256r1")

# Verify signature
is_valid = hybrid_verify(message, signature, ecdsa_pub, dilithium_pub)
print(f"Signature valid: {is_valid}")
```

#### Compact Signatures

```python
from src import create_compact_hybrid_signature, verify_compact_hybrid_signature

# Create compact signature
compact_sig = create_compact_hybrid_signature(
    message, ecdsa_priv, dilithium_priv, "secp256r1"
)

# Verify compact signature
is_valid = verify_compact_hybrid_signature(
    message, compact_sig, ecdsa_pub, dilithium_pub, 64
)
```

---

## ⚙️ Advanced Features

### 1. Key Exchange Packages

```python
from src import create_hybrid_key_exchange_package

# Create complete package
package = create_hybrid_key_exchange_package(rsa_pub, kyber_pub, "RSA")

print("Package contents:")
for key, value in package.items():
    print(f"  {key}: {value}")
```

### 2. Signature Information

```python
from src import get_signature_info, export_signature_to_json

# Get signature information
info = get_signature_info(signature)
print("Signature info:", info)

# Export to JSON
json_sig = export_signature_to_json(signature)
print("JSON signature:", json_sig)
```

### 3. Different Security Levels

```python
# Kyber security levels
kyber_levels = ["Kyber512", "Kyber768", "Kyber1024"]
for level in kyber_levels:
    pub, priv = generate_kyber_keys(level)
    # Use different levels for different security requirements

# Dilithium security levels
dilithium_levels = ["Dilithium2", "Dilithium3", "Dilithium5"]
for level in dilithium_levels:
    pub, priv = generate_dilithium_keys(level)
    # Use different levels for different security requirements
```

### 4. Utility Functions

```python
from src import (
    shake256_hash, 
    hkdf_derive_key, 
    encode_base64, 
    decode_base64,
    generate_random_bytes
)

# SHAKE256 hashing
hash_result = shake256_hash(b"data to hash", 32)

# HKDF key derivation
derived_key = hkdf_derive_key(b"secret", salt=b"salt", info=b"info")

# Base64 encoding/decoding
encoded = encode_base64(b"binary data")
decoded = decode_base64(encoded)

# Random bytes generation
random_data = generate_random_bytes(32)
```

---

## 🌐 API Usage

### Starting the API

```bash
# Run the API directly
python examples/api_example.py

# Or using Docker
docker run -p 8000:8000 rights-to-secure-hybrid-crypto
```

### API Endpoints

#### 1. Health Check

```bash
curl http://localhost:8000/health
```

#### 2. Generate Keys

```bash
curl -X POST http://localhost:8000/keys/generate \
  -H "Content-Type: application/json" \
  -d '{
    "classical_type": "RSA",
    "rsa_key_size": 2048,
    "kyber_level": "Kyber512"
  }'
```

#### 3. Perform Key Exchange

```bash
curl -X POST http://localhost:8000/keys/exchange \
  -H "Content-Type: application/json" \
  -d '{
    "classical_type": "RSA",
    "rsa_key_size": 2048,
    "kyber_level": "Kyber512"
  }'
```

#### 4. Create Signature

```bash
curl -X POST http://localhost:8000/sign \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test message",
    "ecdsa_curve": "secp256r1",
    "dilithium_level": "Dilithium2"
  }'
```

#### 5. Verify Signature

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test message",
    "signature": {...},
    "ecdsa_public_key": "...",
    "dilithium_public_key": "..."
  }'
```

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🐳 Docker Deployment

### Basic Docker Usage

```bash
# Build image
docker build -t rights-to-secure-hybrid-crypto .

# Run container
docker run -p 8000:8000 rights-to-secure-hybrid-crypto

# Run with custom command
docker run rights-to-secure-hybrid-crypto python examples/demo_key_exchange.py
```

### Docker Compose

```bash
# Start API service
docker-compose up hybrid-crypto-api

# Start development environment
docker-compose --profile dev up

# Run tests
docker-compose --profile test up

# Run demos
docker-compose --profile demo up

# Start production stack
docker-compose --profile production up
```

### Production Deployment

```bash
# Create production environment
docker-compose --profile production up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f hybrid-crypto-api

# Scale services
docker-compose up -d --scale hybrid-crypto-api=3
```

---

## 🧪 Testing

### Run All Tests

```bash
# Using pytest directly
pytest tests/ -v

# Using Docker
docker-compose --profile test up

# Run specific test file
pytest tests/test_hybrid_kem.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Test Categories

```bash
# Key exchange tests
pytest tests/test_hybrid_kem.py::TestHybridKEM::test_rsa_kyber_key_exchange

# Signature tests
pytest tests/test_hybrid_signature.py::TestHybridSignature::test_hybrid_signature_creation

# Utility tests
pytest tests/ -k "utils"
```

### Manual Testing

```bash
# Run key exchange demo
python examples/demo_key_exchange.py

# Run signature demo
python examples/demo_signing.py

# Run API demo
python examples/api_example.py
```

---

## 🔒 Security Best Practices

### 1. Key Management

```python
# ✅ Good: Use secure key generation
from src import generate_rsa_keys, generate_kyber_keys

# Generate keys with appropriate sizes
rsa_pub, rsa_priv = generate_rsa_keys(2048)  # Minimum 2048 bits
kyber_pub, kyber_priv = generate_kyber_keys("Kyber512")

# ❌ Bad: Don't use weak key sizes
rsa_pub, rsa_priv = generate_rsa_keys(1024)  # Too weak
```

### 2. Key Storage

```python
# ✅ Good: Store keys securely
import os
from cryptography.fernet import Fernet

# Encrypt private keys before storage
key = Fernet.generate_key()
cipher = Fernet(key)
encrypted_private_key = cipher.encrypt(rsa_priv)

# ❌ Bad: Don't store keys in plain text
with open("private_key.pem", "wb") as f:
    f.write(rsa_priv)  # Unencrypted storage
```

### 3. Session Key Usage

```python
# ✅ Good: Use session keys for symmetric encryption
from cryptography.fernet import Fernet

# Derive encryption key from session key
encryption_key = session_key[:32]  # Use first 32 bytes
cipher = Fernet(encryption_key)

# Encrypt data
encrypted_data = cipher.encrypt(b"sensitive data")

# ❌ Bad: Don't reuse session keys
# Use each session key only once
```

### 4. Signature Verification

```python
# ✅ Good: Always verify signatures
is_valid = hybrid_verify(message, signature, ecdsa_pub, dilithium_pub)
if not is_valid:
    raise ValueError("Invalid signature")

# ❌ Bad: Don't skip verification
# Always verify signatures before processing
```

### 5. Error Handling

```python
# ✅ Good: Handle errors gracefully
try:
    session_key = hybrid_key_decrypt(rsa_priv, kyber_priv, rsa_ct, kyber_ct, "RSA")
except Exception as e:
    logger.error(f"Key decryption failed: {e}")
    # Handle error appropriately

# ❌ Bad: Don't ignore errors
session_key = hybrid_key_decrypt(rsa_priv, kyber_priv, rsa_ct, kyber_ct, "RSA")
# No error handling
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Problem: Module not found
ModuleNotFoundError: No module named 'src'

# Solution: Add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/hybrid-crypto/src"
```

#### 2. OQS Library Issues

```bash
# Problem: OQS library not found
ImportError: No module named 'oqs'

# Solution: Install OQS Python
pip install oqs-python
```

#### 3. Cryptography Library Issues

```bash
# Problem: Cryptography library errors
ImportError: No module named 'cryptography'

# Solution: Install cryptography
pip install cryptography
```

#### 4. Docker Build Issues

```bash
# Problem: Build fails
ERROR: Failed to build wheel for oqs-python

# Solution: Install build dependencies
apt-get update && apt-get install -y build-essential libssl-dev libffi-dev
```

### Performance Issues

#### 1. Slow Key Generation

```python
# Problem: Key generation is slow
# Solution: Use appropriate key sizes
rsa_pub, rsa_priv = generate_rsa_keys(2048)  # Good balance
# Avoid 4096+ for development
```

#### 2. Large Signature Sizes

```python
# Problem: Signatures are too large
# Solution: Use compact signatures
compact_sig = create_compact_hybrid_signature(message, ecdsa_priv, dilithium_priv)
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with verbose output
python -v examples/demo_key_exchange.py
```

---

## 📞 Support

### Getting Help

- **Documentation**: https://academy.rightstosecure.com
- **Email**: contact@arkaenterprises.com
- **Phone**: +1 314-624-8101
- **Website**: https://rightstosecure.com

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### License

MIT License - see LICENSE file for details.

---

## 🎯 Next Steps

1. **Explore Examples**: Run the demo scripts
2. **Read Documentation**: Check the API docs
3. **Run Tests**: Verify everything works
4. **Deploy**: Use Docker for production
5. **Integrate**: Add to your application

---

*For more information, visit [https://rightstosecure.com](https://rightstosecure.com)* 