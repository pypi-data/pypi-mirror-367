"""
RightsToSecure Hybrid Crypto Wrapper - KEM Tests
Test suite for hybrid key encapsulation mechanism.
"""

import sys
import os
import pytest
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from hybrid_kem import (
    hybrid_key_exchange,
    hybrid_key_decrypt,
    create_hybrid_key_exchange_package,
    verify_hybrid_key_exchange
)
from utils import (
    generate_rsa_keys,
    generate_ecdsa_keys,
    generate_kyber_keys,
    encode_base64,
    decode_base64
)


class TestHybridKEM:
    """Test cases for hybrid key encapsulation mechanism."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Generate test keys
        self.rsa_pub, self.rsa_priv = generate_rsa_keys(2048)
        self.ecc_pub, self.ecc_priv = generate_ecdsa_keys("secp256r1")
        self.kyber_pub, self.kyber_priv = generate_kyber_keys("Kyber512")
    
    def test_rsa_kyber_key_exchange(self):
        """Test RSA + Kyber hybrid key exchange."""
        # Perform key exchange
        rsa_ct, kyber_ct, session_key = hybrid_key_exchange(
            self.rsa_pub, self.kyber_pub, "RSA"
        )
        
        # Verify outputs
        assert isinstance(rsa_ct, str)
        assert isinstance(kyber_ct, str)
        assert isinstance(session_key, bytes)
        assert len(session_key) == 32  # 256-bit key
        
        # Reconstruct session key
        reconstructed_key = hybrid_key_decrypt(
            self.rsa_priv, self.kyber_priv, rsa_ct, kyber_ct, "RSA"
        )
        
        # Verify keys match
        assert session_key == reconstructed_key
    
    def test_ecc_kyber_key_exchange(self):
        """Test ECC + Kyber hybrid key exchange."""
        # Perform key exchange
        ecc_ct, kyber_ct, session_key = hybrid_key_exchange(
            self.ecc_pub, self.kyber_pub, "ECC"
        )
        
        # Verify outputs
        assert isinstance(ecc_ct, str)
        assert isinstance(kyber_ct, str)
        assert isinstance(session_key, bytes)
        assert len(session_key) == 32  # 256-bit key
        
        # Reconstruct session key
        reconstructed_key = hybrid_key_decrypt(
            self.ecc_priv, self.kyber_priv, ecc_ct, kyber_ct, "ECC"
        )
        
        # Verify keys match
        assert session_key == reconstructed_key
    
    def test_invalid_classical_type(self):
        """Test handling of invalid classical key type."""
        with pytest.raises(ValueError, match="Unsupported classical type"):
            hybrid_key_exchange(self.rsa_pub, self.kyber_pub, "INVALID")
    
    def test_key_exchange_package_creation(self):
        """Test creation of key exchange package."""
        package = create_hybrid_key_exchange_package(
            self.rsa_pub, self.kyber_pub, "RSA"
        )
        
        # Verify package structure
        assert "classical_ciphertext" in package
        assert "kyber_ciphertext" in package
        assert "session_key" in package
        assert "classical_type" in package
        assert "version" in package
        assert "algorithm" in package
        
        # Verify values
        assert package["classical_type"] == "RSA"
        assert package["version"] == "1.0"
        assert package["algorithm"] == "RightsToSecure-Hybrid-KEM"
        
        # Verify session key is base64 encoded
        session_key_bytes = decode_base64(package["session_key"])
        assert len(session_key_bytes) == 32
    
    def test_multiple_key_exchanges(self):
        """Test multiple key exchanges produce different session keys."""
        # First key exchange
        rsa_ct1, kyber_ct1, session_key1 = hybrid_key_exchange(
            self.rsa_pub, self.kyber_pub, "RSA"
        )
        
        # Second key exchange
        rsa_ct2, kyber_ct2, session_key2 = hybrid_key_exchange(
            self.rsa_pub, self.kyber_pub, "RSA"
        )
        
        # Verify different session keys
        assert session_key1 != session_key2
        
        # Verify different ciphertexts
        assert rsa_ct1 != rsa_ct2
        assert kyber_ct1 != kyber_ct2
    
    def test_key_exchange_with_different_kyber_levels(self):
        """Test key exchange with different Kyber security levels."""
        # Generate Kyber keys with different levels
        kyber_pub_512, kyber_priv_512 = generate_kyber_keys("Kyber512")
        kyber_pub_768, kyber_priv_768 = generate_kyber_keys("Kyber768")
        kyber_pub_1024, kyber_priv_1024 = generate_kyber_keys("Kyber1024")
        
        # Test each level
        for pub, priv in [(kyber_pub_512, kyber_priv_512),
                         (kyber_pub_768, kyber_priv_768),
                         (kyber_pub_1024, kyber_priv_1024)]:
            
            rsa_ct, kyber_ct, session_key = hybrid_key_exchange(
                self.rsa_pub, pub, "RSA"
            )
            
            reconstructed_key = hybrid_key_decrypt(
                self.rsa_priv, priv, rsa_ct, kyber_ct, "RSA"
            )
            
            assert session_key == reconstructed_key
            assert len(session_key) == 32
    
    def test_key_exchange_with_different_rsa_sizes(self):
        """Test key exchange with different RSA key sizes."""
        # Generate RSA keys with different sizes
        rsa_pub_1024, rsa_priv_1024 = generate_rsa_keys(1024)
        rsa_pub_2048, rsa_priv_2048 = generate_rsa_keys(2048)
        rsa_pub_4096, rsa_priv_4096 = generate_rsa_keys(4096)
        
        # Test each size
        for pub, priv in [(rsa_pub_1024, rsa_priv_1024),
                         (rsa_pub_2048, rsa_priv_2048),
                         (rsa_pub_4096, rsa_priv_4096)]:
            
            rsa_ct, kyber_ct, session_key = hybrid_key_exchange(
                pub, self.kyber_pub, "RSA"
            )
            
            reconstructed_key = hybrid_key_decrypt(
                priv, self.kyber_priv, rsa_ct, kyber_ct, "RSA"
            )
            
            assert session_key == reconstructed_key
            assert len(session_key) == 32
    
    def test_key_exchange_with_different_ecc_curves(self):
        """Test key exchange with different ECC curves."""
        # Generate ECC keys with different curves
        ecc_pub_256, ecc_priv_256 = generate_ecdsa_keys("secp256r1")
        ecc_pub_384, ecc_priv_384 = generate_ecdsa_keys("secp384r1")
        ecc_pub_521, ecc_priv_521 = generate_ecdsa_keys("secp521r1")
        
        # Test each curve
        for pub, priv in [(ecc_pub_256, ecc_priv_256),
                         (ecc_pub_384, ecc_priv_384),
                         (ecc_pub_521, ecc_priv_521)]:
            
            ecc_ct, kyber_ct, session_key = hybrid_key_exchange(
                pub, self.kyber_pub, "ECC"
            )
            
            reconstructed_key = hybrid_key_decrypt(
                priv, self.kyber_priv, ecc_ct, kyber_ct, "ECC"
            )
            
            assert session_key == reconstructed_key
            assert len(session_key) == 32
    
    def test_invalid_ciphertext_decryption(self):
        """Test decryption with invalid ciphertext."""
        # Create valid key exchange
        rsa_ct, kyber_ct, session_key = hybrid_key_exchange(
            self.rsa_pub, self.kyber_pub, "RSA"
        )
        
        # Try to decrypt with invalid ciphertext
        with pytest.raises(Exception):
            hybrid_key_decrypt(
                self.rsa_priv, self.kyber_priv, "invalid", kyber_ct, "RSA"
            )
        
        with pytest.raises(Exception):
            hybrid_key_decrypt(
                self.rsa_priv, self.kyber_priv, rsa_ct, "invalid", "RSA"
            )
    
    def test_session_key_uniqueness(self):
        """Test that session keys are cryptographically unique."""
        session_keys = set()
        
        # Generate multiple session keys
        for _ in range(10):
            _, _, session_key = hybrid_key_exchange(
                self.rsa_pub, self.kyber_pub, "RSA"
            )
            session_keys.add(session_key.hex())
        
        # Verify all keys are unique
        assert len(session_keys) == 10
    
    def test_base64_encoding_consistency(self):
        """Test that base64 encoding/decoding is consistent."""
        rsa_ct, kyber_ct, session_key = hybrid_key_exchange(
            self.rsa_pub, self.kyber_pub, "RSA"
        )
        
        # Verify ciphertexts are valid base64
        try:
            decode_base64(rsa_ct)
            decode_base64(kyber_ct)
        except Exception:
            pytest.fail("Ciphertexts are not valid base64")
        
        # Verify session key can be base64 encoded
        session_key_b64 = encode_base64(session_key)
        decoded_key = decode_base64(session_key_b64)
        assert session_key == decoded_key


if __name__ == "__main__":
    pytest.main([__file__]) 