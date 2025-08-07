"""
RightsToSecure Hybrid Crypto Wrapper - Signature Tests
Test suite for hybrid digital signatures.
"""

import sys
import os
import pytest
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from hybrid_signature import (
    hybrid_sign,
    hybrid_verify,
    create_compact_hybrid_signature,
    verify_compact_hybrid_signature,
    get_signature_info,
    export_signature_to_json,
    import_signature_from_json
)
from utils import (
    generate_ecdsa_keys,
    generate_dilithium_keys,
    encode_base64,
    decode_base64
)


class TestHybridSignature:
    """Test cases for hybrid digital signatures."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Generate test keys
        self.ecdsa_pub, self.ecdsa_priv = generate_ecdsa_keys("secp256r1")
        self.dilithium_pub, self.dilithium_priv = generate_dilithium_keys("Dilithium2")
        
        # Test messages
        self.test_message = "Test message for hybrid signature"
        self.test_message_bytes = self.test_message.encode('utf-8')
    
    def test_hybrid_signature_creation(self):
        """Test creation of hybrid signature."""
        # Create signature
        signature = hybrid_sign(
            self.test_message, self.ecdsa_priv, self.dilithium_priv, "secp256r1"
        )
        
        # Verify signature structure
        assert "ecdsa_signature" in signature
        assert "dilithium_signature" in signature
        assert "message_hash" in signature
        assert "version" in signature
        assert "algorithm" in signature
        assert "ecdsa_curve" in signature
        assert "dilithium_level" in signature
        
        # Verify values
        assert signature["version"] == "1.0"
        assert signature["algorithm"] == "RightsToSecure-Hybrid-Signature"
        assert signature["ecdsa_curve"] == "secp256r1"
        assert signature["dilithium_level"] == "Dilithium2"
        
        # Verify signature components are base64 encoded
        ecdsa_sig = decode_base64(signature["ecdsa_signature"])
        dilithium_sig = decode_base64(signature["dilithium_signature"])
        message_hash = decode_base64(signature["message_hash"])
        
        assert len(ecdsa_sig) > 0
        assert len(dilithium_sig) > 0
        assert len(message_hash) == 32  # SHA-256 hash
    
    def test_hybrid_signature_verification(self):
        """Test verification of hybrid signature."""
        # Create signature
        signature = hybrid_sign(
            self.test_message, self.ecdsa_priv, self.dilithium_priv, "secp256r1"
        )
        
        # Verify signature
        is_valid = hybrid_verify(
            self.test_message, signature, self.ecdsa_pub, self.dilithium_pub
        )
        
        assert is_valid is True
    
    def test_signature_with_bytes_message(self):
        """Test signature creation and verification with bytes message."""
        # Create signature with bytes
        signature = hybrid_sign(
            self.test_message_bytes, self.ecdsa_priv, self.dilithium_priv, "secp256r1"
        )
        
        # Verify signature with bytes
        is_valid = hybrid_verify(
            self.test_message_bytes, signature, self.ecdsa_pub, self.dilithium_pub
        )
        
        assert is_valid is True
    
    def test_compact_signature_creation(self):
        """Test creation of compact hybrid signature."""
        # Create compact signature
        compact_sig = create_compact_hybrid_signature(
            self.test_message, self.ecdsa_priv, self.dilithium_priv, "secp256r1"
        )
        
        # Verify it's base64 encoded
        assert isinstance(compact_sig, str)
        
        # Decode and verify structure
        decoded_sig = decode_base64(compact_sig)
        assert len(decoded_sig) > 64  # Should be longer than just ECDSA signature
    
    def test_compact_signature_verification(self):
        """Test verification of compact hybrid signature."""
        # Create compact signature
        compact_sig = create_compact_hybrid_signature(
            self.test_message, self.ecdsa_priv, self.dilithium_priv, "secp256r1"
        )
        
        # Verify compact signature
        is_valid = verify_compact_hybrid_signature(
            self.test_message, compact_sig, self.ecdsa_pub, self.dilithium_pub, 64
        )
        
        assert is_valid is True
    
    def test_signature_tampering_detection(self):
        """Test detection of signature tampering."""
        # Create original signature
        original_sig = hybrid_sign(
            self.test_message, self.ecdsa_priv, self.dilithium_priv, "secp256r1"
        )
        
        # Test 1: Tamper with message
        tampered_message = "Tampered message for hybrid signature"
        is_valid_tampered = hybrid_verify(
            tampered_message, original_sig, self.ecdsa_pub, self.dilithium_pub
        )
        assert is_valid_tampered is False
        
        # Test 2: Tamper with signature
        tampered_sig = original_sig.copy()
        tampered_sig["ecdsa_signature"] = "tampered_data"
        is_valid_tampered_sig = hybrid_verify(
            self.test_message, tampered_sig, self.ecdsa_pub, self.dilithium_pub
        )
        assert is_valid_tampered_sig is False
        
        # Test 3: Remove signature component
        incomplete_sig = original_sig.copy()
        del incomplete_sig["ecdsa_signature"]
        is_valid_incomplete = hybrid_verify(
            self.test_message, incomplete_sig, self.ecdsa_pub, self.dilithium_pub
        )
        assert is_valid_incomplete is False
    
    def test_signature_info_extraction(self):
        """Test extraction of signature information."""
        # Create signature
        signature = hybrid_sign(
            self.test_message, self.ecdsa_priv, self.dilithium_priv, "secp256r1"
        )
        
        # Extract info
        info = get_signature_info(signature)
        
        # Verify info structure
        assert "version" in info
        assert "algorithm" in info
        assert "ecdsa_curve" in info
        assert "dilithium_level" in info
        assert "ecdsa_signature_length" in info
        assert "dilithium_signature_length" in info
        assert "total_signature_length" in info
        
        # Verify values
        assert info["version"] == "1.0"
        assert info["algorithm"] == "RightsToSecure-Hybrid-Signature"
        assert info["ecdsa_curve"] == "secp256r1"
        assert info["dilithium_level"] == "Dilithium2"
        assert info["ecdsa_signature_length"] > 0
        assert info["dilithium_signature_length"] > 0
        assert info["total_signature_length"] > 0
    
    def test_json_export_import(self):
        """Test JSON export and import of signatures."""
        # Create signature
        original_sig = hybrid_sign(
            self.test_message, self.ecdsa_priv, self.dilithium_priv, "secp256r1"
        )
        
        # Export to JSON
        json_sig = export_signature_to_json(original_sig)
        
        # Verify JSON is valid
        assert isinstance(json_sig, str)
        parsed_json = json.loads(json_sig)
        assert parsed_json == original_sig
        
        # Import from JSON
        imported_sig = import_signature_from_json(json_sig)
        
        # Verify imported signature matches original
        assert imported_sig == original_sig
        
        # Verify imported signature is still valid
        is_valid = hybrid_verify(
            self.test_message, imported_sig, self.ecdsa_pub, self.dilithium_pub
        )
        assert is_valid is True
    
    def test_different_ecc_curves(self):
        """Test signatures with different ECC curves."""
        curves = ["secp256r1", "secp384r1", "secp521r1"]
        
        for curve in curves:
            # Generate keys for this curve
            ecdsa_pub, ecdsa_priv = generate_ecdsa_keys(curve)
            
            # Create signature
            signature = hybrid_sign(
                self.test_message, ecdsa_priv, self.dilithium_priv, curve
            )
            
            # Verify signature
            is_valid = hybrid_verify(
                self.test_message, signature, ecdsa_pub, self.dilithium_pub
            )
            
            assert is_valid is True
            assert signature["ecdsa_curve"] == curve
    
    def test_different_dilithium_levels(self):
        """Test signatures with different Dilithium security levels."""
        levels = ["Dilithium2", "Dilithium3", "Dilithium5"]
        
        for level in levels:
            # Generate keys for this level
            dilithium_pub, dilithium_priv = generate_dilithium_keys(level)
            
            # Create signature
            signature = hybrid_sign(
                self.test_message, self.ecdsa_priv, dilithium_priv, "secp256r1"
            )
            
            # Verify signature
            is_valid = hybrid_verify(
                self.test_message, signature, self.ecdsa_pub, dilithium_pub
            )
            
            assert is_valid is True
            assert signature["dilithium_level"] == level
    
    def test_multiple_signatures_uniqueness(self):
        """Test that multiple signatures of the same message are unique."""
        signatures = []
        
        # Create multiple signatures
        for _ in range(5):
            sig = hybrid_sign(
                self.test_message, self.ecdsa_priv, self.dilithium_priv, "secp256r1"
            )
            signatures.append(sig)
        
        # Verify all signatures are unique
        signature_strings = [json.dumps(sig, sort_keys=True) for sig in signatures]
        unique_signatures = set(signature_strings)
        
        assert len(unique_signatures) == 5
    
    def test_large_message_signature(self):
        """Test signature creation and verification with large message."""
        # Create large message
        large_message = "A" * 10000  # 10KB message
        
        # Create signature
        signature = hybrid_sign(
            large_message, self.ecdsa_priv, self.dilithium_priv, "secp256r1"
        )
        
        # Verify signature
        is_valid = hybrid_verify(
            large_message, signature, self.ecdsa_pub, self.dilithium_pub
        )
        
        assert is_valid is True
    
    def test_empty_message_signature(self):
        """Test signature creation and verification with empty message."""
        empty_message = ""
        
        # Create signature
        signature = hybrid_sign(
            empty_message, self.ecdsa_priv, self.dilithium_priv, "secp256r1"
        )
        
        # Verify signature
        is_valid = hybrid_verify(
            empty_message, signature, self.ecdsa_pub, self.dilithium_pub
        )
        
        assert is_valid is True
    
    def test_unicode_message_signature(self):
        """Test signature creation and verification with Unicode message."""
        unicode_message = "Hello, 世界! 🌍 こんにちは! Привет!"
        
        # Create signature
        signature = hybrid_sign(
            unicode_message, self.ecdsa_priv, self.dilithium_priv, "secp256r1"
        )
        
        # Verify signature
        is_valid = hybrid_verify(
            unicode_message, signature, self.ecdsa_pub, self.dilithium_pub
        )
        
        assert is_valid is True
    
    def test_invalid_compact_signature_length(self):
        """Test compact signature verification with invalid ECDSA signature length."""
        # Create compact signature
        compact_sig = create_compact_hybrid_signature(
            self.test_message, self.ecdsa_priv, self.dilithium_priv, "secp256r1"
        )
        
        # Try to verify with wrong ECDSA signature length
        with pytest.raises(Exception):
            verify_compact_hybrid_signature(
                self.test_message, compact_sig, self.ecdsa_pub, self.dilithium_pub, 32
            )
    
    def test_invalid_json_import(self):
        """Test import of invalid JSON signature."""
        invalid_json = '{"invalid": "signature"}'
        
        with pytest.raises(Exception):
            hybrid_verify(
                self.test_message, 
                import_signature_from_json(invalid_json), 
                self.ecdsa_pub, 
                self.dilithium_pub
            )


if __name__ == "__main__":
    pytest.main([__file__]) 