"""
RightsToSecure Hybrid Crypto Wrapper - Main Package
Quantum-resistant hybrid cryptography library.
"""

__version__ = "1.0.0"
__author__ = "Praveen Naidu"
__email__ = "contact@arkaenterprises.com"
__url__ = "https://rightstosecure.com"

# Import main functions for easy access
from .hybrid_kem import (
    hybrid_key_exchange,
    hybrid_key_decrypt,
    create_hybrid_key_exchange_package,
    verify_hybrid_key_exchange
)

from .hybrid_signature import (
    hybrid_sign,
    hybrid_verify,
    create_compact_hybrid_signature,
    verify_compact_hybrid_signature,
    get_signature_info,
    export_signature_to_json,
    import_signature_from_json
)

from .utils import (
    generate_rsa_keys,
    generate_ecdsa_keys,
    generate_kyber_keys,
    generate_dilithium_keys,
    shake256_hash,
    hkdf_derive_key,
    encode_base64,
    decode_base64,
    generate_random_bytes,
    combine_secrets
)

__all__ = [
    # Version and metadata
    "__version__",
    "__author__",
    "__email__",
    "__url__",
    
    # Key Exchange functions
    "hybrid_key_exchange",
    "hybrid_key_decrypt",
    "create_hybrid_key_exchange_package",
    "verify_hybrid_key_exchange",
    
    # Signature functions
    "hybrid_sign",
    "hybrid_verify",
    "create_compact_hybrid_signature",
    "verify_compact_hybrid_signature",
    "get_signature_info",
    "export_signature_to_json",
    "import_signature_from_json",
    
    # Utility functions
    "generate_rsa_keys",
    "generate_ecdsa_keys",
    "generate_kyber_keys",
    "generate_dilithium_keys",
    "shake256_hash",
    "hkdf_derive_key",
    "encode_base64",
    "decode_base64",
    "generate_random_bytes",
    "combine_secrets",
] 