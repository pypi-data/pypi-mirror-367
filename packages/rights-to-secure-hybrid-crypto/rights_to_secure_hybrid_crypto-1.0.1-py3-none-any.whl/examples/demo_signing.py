#!/usr/bin/env python3
"""
RightsToSecure Hybrid Crypto Wrapper - Digital Signature Demo
Demonstrates ECDSA + Dilithium hybrid digital signature functionality.
"""

import sys
import os
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
from utils import generate_ecdsa_keys, generate_dilithium_keys


def demo_hybrid_signature():
    """Demonstrate ECDSA + Dilithium hybrid signature."""
    print("✍️ RightsToSecure Hybrid Digital Signature Demo")
    print("=" * 55)
    print("Algorithm: ECDSA + Dilithium")
    print()
    
    # Generate key pairs
    print("📋 Generating key pairs...")
    ecdsa_pub, ecdsa_priv = generate_ecdsa_keys("secp256r1")
    dilithium_pub, dilithium_priv = generate_dilithium_keys("Dilithium2")
    
    print(f"✅ ECDSA Public Key: {len(ecdsa_pub)} bytes")
    print(f"✅ ECDSA Private Key: {len(ecdsa_priv)} bytes")
    print(f"✅ Dilithium Public Key: {len(dilithium_pub)} bytes")
    print(f"✅ Dilithium Private Key: {len(dilithium_priv)} bytes")
    print()
    
    # Message to sign
    message = "Confidential data for RightsToSecure - Quantum-resistant hybrid signature"
    print(f"📝 Message: {message}")
    print(f"📏 Message length: {len(message)} characters")
    print()
    
    # Create hybrid signature
    print("✍️ Creating hybrid signature...")
    hybrid_sig = hybrid_sign(message, ecdsa_priv, dilithium_priv, "secp256r1")
    
    print("📋 Signature Components:")
    for key, value in hybrid_sig.items():
        if key in ["ecdsa_signature", "dilithium_signature", "message_hash"]:
            print(f"  {key}: {len(value)} chars (base64)")
        else:
            print(f"  {key}: {value}")
    print()
    
    # Verify hybrid signature
    print("🔍 Verifying hybrid signature...")
    is_valid = hybrid_verify(message, hybrid_sig, ecdsa_pub, dilithium_pub)
    
    if is_valid:
        print("✅ SUCCESS: Hybrid signature is valid!")
    else:
        print("❌ ERROR: Hybrid signature verification failed!")
    
    print()
    return hybrid_sig, is_valid


def demo_compact_signature():
    """Demonstrate compact hybrid signature format."""
    print("📦 RightsToSecure Compact Signature Demo")
    print("=" * 45)
    print()
    
    # Generate key pairs
    print("📋 Generating key pairs...")
    ecdsa_pub, ecdsa_priv = generate_ecdsa_keys("secp256r1")
    dilithium_pub, dilithium_priv = generate_dilithium_keys("Dilithium2")
    
    # Message to sign
    message = "Compact hybrid signature test message"
    print(f"📝 Message: {message}")
    print()
    
    # Create compact signature
    print("📦 Creating compact signature...")
    compact_sig = create_compact_hybrid_signature(
        message, ecdsa_priv, dilithium_priv, "secp256r1"
    )
    
    print(f"✅ Compact Signature: {len(compact_sig)} chars (base64)")
    print(f"✅ Signature (first 50 chars): {compact_sig[:50]}...")
    print()
    
    # Verify compact signature
    print("🔍 Verifying compact signature...")
    is_valid = verify_compact_hybrid_signature(
        message, compact_sig, ecdsa_pub, dilithium_pub, 64
    )
    
    if is_valid:
        print("✅ SUCCESS: Compact signature is valid!")
    else:
        print("❌ ERROR: Compact signature verification failed!")
    
    print()
    return compact_sig, is_valid


def demo_signature_manipulation():
    """Demonstrate signature manipulation and export/import."""
    print("🔄 RightsToSecure Signature Manipulation Demo")
    print("=" * 50)
    print()
    
    # Generate key pairs
    print("📋 Generating key pairs...")
    ecdsa_pub, ecdsa_priv = generate_ecdsa_keys("secp256r1")
    dilithium_pub, dilithium_priv = generate_dilithium_keys("Dilithium2")
    
    # Create signature
    message = "Signature manipulation test"
    print(f"📝 Message: {message}")
    print()
    
    hybrid_sig = hybrid_sign(message, ecdsa_priv, dilithium_priv, "secp256r1")
    
    # Get signature info
    print("📊 Signature Information:")
    sig_info = get_signature_info(hybrid_sig)
    for key, value in sig_info.items():
        print(f"  {key}: {value}")
    print()
    
    # Export to JSON
    print("📤 Exporting signature to JSON...")
    json_sig = export_signature_to_json(hybrid_sig)
    print(f"✅ JSON Signature: {len(json_sig)} characters")
    print(f"✅ JSON Preview: {json_sig[:100]}...")
    print()
    
    # Import from JSON
    print("📥 Importing signature from JSON...")
    imported_sig = import_signature_from_json(json_sig)
    
    # Verify imported signature
    print("🔍 Verifying imported signature...")
    is_valid = hybrid_verify(message, imported_sig, ecdsa_pub, dilithium_pub)
    
    if is_valid:
        print("✅ SUCCESS: Imported signature is valid!")
    else:
        print("❌ ERROR: Imported signature verification failed!")
    
    print()
    return json_sig, is_valid


def demo_signature_tampering():
    """Demonstrate signature tampering detection."""
    print("🚨 RightsToSecure Tampering Detection Demo")
    print("=" * 50)
    print()
    
    # Generate key pairs
    print("📋 Generating key pairs...")
    ecdsa_pub, ecdsa_priv = generate_ecdsa_keys("secp256r1")
    dilithium_pub, dilithium_priv = generate_dilithium_keys("Dilithium2")
    
    # Create signature
    original_message = "Original message for tampering test"
    print(f"📝 Original Message: {original_message}")
    print()
    
    hybrid_sig = hybrid_sign(original_message, ecdsa_priv, dilithium_priv, "secp256r1")
    
    # Test 1: Verify original signature
    print("🔍 Test 1: Verifying original signature...")
    is_valid_original = hybrid_verify(original_message, hybrid_sig, ecdsa_pub, dilithium_pub)
    print(f"✅ Original signature valid: {is_valid_original}")
    print()
    
    # Test 2: Tamper with message
    tampered_message = "Tampered message for tampering test"
    print(f"📝 Tampered Message: {tampered_message}")
    print("🔍 Test 2: Verifying tampered message...")
    is_valid_tampered = hybrid_verify(tampered_message, hybrid_sig, ecdsa_pub, dilithium_pub)
    print(f"✅ Tampered message valid: {is_valid_tampered}")
    print()
    
    # Test 3: Tamper with signature
    print("🔍 Test 3: Verifying tampered signature...")
    tampered_sig = hybrid_sig.copy()
    tampered_sig["ecdsa_signature"] = "tampered_signature_data"
    is_valid_tampered_sig = hybrid_verify(original_message, tampered_sig, ecdsa_pub, dilithium_pub)
    print(f"✅ Tampered signature valid: {is_valid_tampered_sig}")
    print()
    
    print("🎯 Tampering Detection Results:")
    print(f"  • Original signature: {'✅ Valid' if is_valid_original else '❌ Invalid'}")
    print(f"  • Tampered message: {'✅ Valid' if is_valid_tampered else '❌ Invalid'}")
    print(f"  • Tampered signature: {'✅ Valid' if is_valid_tampered_sig else '❌ Invalid'}")
    print()
    
    return is_valid_original, is_valid_tampered, is_valid_tampered_sig


def main():
    """Run all signature demos."""
    print("🚀 RightsToSecure Hybrid Crypto Wrapper - Digital Signature Demos")
    print("=" * 75)
    print()
    
    try:
        # Demo 1: Basic hybrid signature
        print("Demo 1: ECDSA + Dilithium Hybrid Signature")
        print("-" * 45)
        demo_hybrid_signature()
        
        # Demo 2: Compact signature
        print("Demo 2: Compact Signature Format")
        print("-" * 35)
        demo_compact_signature()
        
        # Demo 3: Signature manipulation
        print("Demo 3: Signature Manipulation")
        print("-" * 35)
        demo_signature_manipulation()
        
        # Demo 4: Tampering detection
        print("Demo 4: Tampering Detection")
        print("-" * 30)
        demo_signature_tampering()
        
        print("🎉 All signature demos completed successfully!")
        print()
        print("💡 Key Features Demonstrated:")
        print("  • ECDSA + Dilithium hybrid signatures")
        print("  • Compact signature format")
        print("  • JSON export/import functionality")
        print("  • Signature information extraction")
        print("  • Tampering detection")
        print()
        print("🔐 Security Features:")
        print("  • Dual signature verification")
        print("  • Message integrity protection")
        print("  • Quantum-resistant Dilithium component")
        print("  • Classical ECDSA compatibility")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 