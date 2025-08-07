# 🔐 RightsToSecure Hybrid Crypto Wrapper

> **Hybrid Post-Quantum Cryptography Library**  
> Developed by **RightsToSecure**  
> Founder: **Praveen Naidu**

---

## 🛡️ Overview

The **RightsToSecure Hybrid Crypto Wrapper** is a cryptographic library designed to combine classical cryptography (RSA/ECDSA) with Post-Quantum Cryptography (Kyber, Dilithium). It provides a quantum-resilient security layer compatible with existing systems, ideal for enterprise SaaS integrations, encrypted messaging, secure file sharing, and API protection.

---

## ✅ Features

- 🔐 **Hybrid Key Exchange** using RSA/ECC + Kyber
- ✍️ **Hybrid Digital Signatures** using ECDSA + Dilithium
- 📦 Compatible with legacy infrastructure (TLS, HTTPS, etc.)
- 🧠 Future-proof against quantum threats
- 🔁 Crypto-agile design for algorithm swapping
- ⚙️ Easy integration as a Python package or API

---

## 📁 Project Structure

```
/rights_to_secure_hybrid_crypto
│
├── /src
│   ├── hybrid_kem.py         # Hybrid Key Exchange logic
│   ├── hybrid_signature.py   # Hybrid Digital Signature logic
│   └── utils.py              # Shared utilities (hashing, KDF, etc.)
│
├── /examples
│   ├── demo_key_exchange.py
│   └── demo_signing.py
│
├── /tests
│   ├── test_hybrid_kem.py
│   └── test_hybrid_signature.py
│
└── README.md
```

---

## 🔐 Hybrid Key Exchange (KEM)

### 🔧 Inputs:
- RSA or ECC Public Key
- Kyber Public Key

### 🔁 Process:
1. Generate a random classical shared secret and encrypt it with RSA or ECC.
2. Use Kyber to encapsulate a PQC shared secret.
3. Concatenate both secrets:
   ```
   combined_secret = classical_secret || pqc_secret
   session_key = SHAKE256(combined_secret)[:32]  # 256-bit
   ```

### 📤 Output:
- `rsa_ciphertext`: RSA-encrypted component
- `kyber_ciphertext`: Kyber-encrypted component
- `session_key`: Final shared key

---

## ✍️ Hybrid Digital Signature

### 🔧 Inputs:
- Message (bytes)
- ECDSA Private Key
- Dilithium Private Key

### 🔁 Process:
1. Sign message with ECDSA → `sig_classical`
2. Sign message with Dilithium → `sig_pqc`
3. Combine both:
   ```
   hybrid_signature = sig_classical || sig_pqc
   ```

### ✅ Verification:
- Validate both parts independently using ECDSA and Dilithium public keys

---

## 🧰 Requirements

### Python Dependencies

```bash
pip install cryptography oqs hashlib
```

#### Libraries Used:
- `cryptography` – for RSA, ECC, and ECDSA
- `oqs-python` – for Kyber and Dilithium (Post-Quantum)
- `hashlib` – for SHAKE256 hashing

---

## 🚀 Usage Examples

### 🔑 Key Exchange

```python
from src.hybrid_kem import hybrid_key_exchange, hybrid_key_decrypt
from src.utils import generate_rsa_keys, generate_kyber_keys

rsa_pub, rsa_priv = generate_rsa_keys()
kyber_pub, kyber_priv = generate_kyber_keys()

# Sender side
rsa_ct, kyber_ct, session_key = hybrid_key_exchange(rsa_pub, kyber_pub)

# Receiver side
session_key_reconstructed = hybrid_key_decrypt(rsa_priv, kyber_priv, rsa_ct, kyber_ct)
```

---

### ✍️ Signature

```python
from src.hybrid_signature import hybrid_sign, hybrid_verify

message = b"Confidential data for RightsToSecure"

# Signing
hybrid_signature = hybrid_sign(message, ecdsa_private_key, dilithium_private_key)

# Verifying
valid = hybrid_verify(message, hybrid_signature, ecdsa_public_key, dilithium_public_key)
print("Signature valid:", valid)
```

---

## 📦 Output Format

- **Base64** encoding for ciphertexts and signatures
- **JSON** objects for hybrid signature structure
- Session keys returned as **raw 256-bit** key (SHAKE256)

---

## 🔧 Packaging and Deployment

- Can be published as a Python package:  
  `rights_to_secure_hybrid_crypto`
- Deployable as a REST API (FastAPI/Flask)
- Docker-compatible for SaaS deployments

---

## 🧪 Testing

### Run Tests

```bash
pytest /tests
```

### Test Coverage:
- RSA + Kyber key encapsulation/decapsulation
- ECDSA + Dilithium hybrid signing/verification
- Key mismatches and edge case validation

---

## 🧱 Roadmap

| Feature | Status |
|--------|--------|
| RSA + Kyber Hybrid KEM | ✅ Completed |
| ECDSA + Dilithium Hybrid Signature | ✅ Completed |
| Falcon Signature Support | 🔜 Planned |
| WASM Module for Web | 🔜 Planned |
| REST API as a Service | 🔜 Planned |
| TLS Handshake Integration | 🔜 Planned |

---

## ⚠️ Security Considerations

- Always use **cryptographically secure** random key generation.
- Use **SHAKE256** or **HKDF** for all KDF operations.
- Never store unencrypted private keys in memory/disk.
- Perform **regular audits** of custom crypto logic.
- Maintain **crypto-agility** to support algorithm replacement.

---

## 📜 License

MIT License (or custom enterprise license for SaaS deployments).  
Contact **RightsToSecure** for commercial use or security audits.

---

## 🧠 About RightsToSecure

**RightsToSecure** is a cybersecurity firm focused on building **quantum-resilient encryption tools** and **secure SaaS solutions** for modern and future internet infrastructure.

### 👨‍💼 Founder: Praveen Naidu

We are committed to helping companies transition to **quantum-safe** cryptography with minimal friction.

🌐 Website: [https://rightstosecure.com](https://rightstosecure.com) quantum proof cyrptoghraphy and secure application development (https://academy.rightstosecure.com) comprehensive real case based scenario based cyber security training 
📧 Email: `contact@arkaenterprises.com`
Phone : +1 314-624-8101

--- 