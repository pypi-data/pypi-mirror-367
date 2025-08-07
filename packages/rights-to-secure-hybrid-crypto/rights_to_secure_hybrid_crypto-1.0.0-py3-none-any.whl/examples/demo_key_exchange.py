#!/usr/bin/env python3
"""
RightsToSecure Hybrid Crypto Wrapper - Key Exchange Demo
Demonstrates RSA + Kyber hybrid key exchange functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from hybrid_kem import hybrid_key_exchange, hybrid_key_decrypt, create_hybrid_key_exchange_package
from utils import generate_rsa_keys, generate_ecdsa_keys, generate_kyber_keys, encode_base64


def demo_rsa_kyber_key_exchange():
    """Demonstrate RSA + Kyber hybrid key exchange."""
    print("🔐 RightsToSecure Hybrid Key Exchange Demo")
    print("=" * 50)
    print("Algorithm: RSA + Kyber")
    print()
    
    # Generate key pairs
    print("📋 Generating key pairs...")
    rsa_pub, rsa_priv = generate_rsa_keys(2048)
    kyber_pub, kyber_priv = generate_kyber_keys("Kyber512")
    
    print(f"✅ RSA Public Key: {len(rsa_pub)} bytes")
    print(f"✅ RSA Private Key: {len(rsa_priv)} bytes")
    print(f"✅ Kyber Public Key: {len(kyber_pub)} bytes")
    print(f"✅ Kyber Private Key: {len(kyber_priv)} bytes")
    print()
    
    # Perform hybrid key exchange (sender side)
    print("🔄 Performing hybrid key exchange...")
    rsa_ct, kyber_ct, session_key = hybrid_key_exchange(
        rsa_pub, kyber_pub, "RSA"
    )
    
    print(f"✅ RSA Ciphertext: {len(rsa_ct)} chars (base64)")
    print(f"✅ Kyber Ciphertext: {len(kyber_ct)} chars (base64)")
    print(f"✅ Session Key: {len(session_key)} bytes")
    print(f"✅ Session Key (hex): {session_key.hex()}")
    print()
    
    # Reconstruct session key (receiver side)
    print("🔓 Reconstructing session key...")
    reconstructed_key = hybrid_key_decrypt(
        rsa_priv, kyber_priv, rsa_ct, kyber_ct, "RSA"
    )
    
    print(f"✅ Reconstructed Key: {len(reconstructed_key)} bytes")
    print(f"✅ Reconstructed Key (hex): {reconstructed_key.hex()}")
    print()
    
    # Verify keys match
    if session_key == reconstructed_key:
        print("🎉 SUCCESS: Session keys match!")
    else:
        print("❌ ERROR: Session keys do not match!")
    
    print()
    return session_key, reconstructed_key


def demo_ecc_kyber_key_exchange():
    """Demonstrate ECC + Kyber hybrid key exchange."""
    print("🔐 RightsToSecure Hybrid Key Exchange Demo")
    print("=" * 50)
    print("Algorithm: ECC + Kyber")
    print()
    
    # Generate key pairs
    print("📋 Generating key pairs...")
    ecc_pub, ecc_priv = generate_ecdsa_keys("secp256r1")
    kyber_pub, kyber_priv = generate_kyber_keys("Kyber512")
    
    print(f"✅ ECC Public Key: {len(ecc_pub)} bytes")
    print(f"✅ ECC Private Key: {len(ecc_priv)} bytes")
    print(f"✅ Kyber Public Key: {len(kyber_pub)} bytes")
    print(f"✅ Kyber Private Key: {len(kyber_priv)} bytes")
    print()
    
    # Perform hybrid key exchange (sender side)
    print("🔄 Performing hybrid key exchange...")
    ecc_ct, kyber_ct, session_key = hybrid_key_exchange(
        ecc_pub, kyber_pub, "ECC"
    )
    
    print(f"✅ ECC Ciphertext: {len(ecc_ct)} chars (base64)")
    print(f"✅ Kyber Ciphertext: {len(kyber_ct)} chars (base64)")
    print(f"✅ Session Key: {len(session_key)} bytes")
    print(f"✅ Session Key (hex): {session_key.hex()}")
    print()
    
    # Reconstruct session key (receiver side)
    print("🔓 Reconstructing session key...")
    reconstructed_key = hybrid_key_decrypt(
        ecc_priv, kyber_priv, ecc_ct, kyber_ct, "ECC"
    )
    
    print(f"✅ Reconstructed Key: {len(reconstructed_key)} bytes")
    print(f"✅ Reconstructed Key (hex): {reconstructed_key.hex()}")
    print()
    
    # Verify keys match
    if session_key == reconstructed_key:
        print("🎉 SUCCESS: Session keys match!")
    else:
        print("❌ ERROR: Session keys do not match!")
    
    print()
    return session_key, reconstructed_key


def demo_key_exchange_package():
    """Demonstrate creating a complete key exchange package."""
    print("📦 RightsToSecure Key Exchange Package Demo")
    print("=" * 50)
    print()
    
    # Generate key pairs
    print("📋 Generating key pairs...")
    rsa_pub, rsa_priv = generate_rsa_keys(2048)
    kyber_pub, kyber_priv = generate_kyber_keys("Kyber512")
    
    # Create complete package
    print("📦 Creating key exchange package...")
    package = create_hybrid_key_exchange_package(rsa_pub, kyber_pub, "RSA")
    
    print("📋 Package Contents:")
    for key, value in package.items():
        if key == "session_key":
            print(f"  {key}: {len(value)} chars (base64)")
        else:
            print(f"  {key}: {value}")
    
    print()
    print("✅ Package created successfully!")
    print()
    
    return package


def main():
    """Run all key exchange demos."""
    print("🚀 RightsToSecure Hybrid Crypto Wrapper - Key Exchange Demos")
    print("=" * 70)
    print()
    
    try:
        # Demo 1: RSA + Kyber
        print("Demo 1: RSA + Kyber Hybrid Key Exchange")
        print("-" * 40)
        demo_rsa_kyber_key_exchange()
        
        # Demo 2: ECC + Kyber
        print("Demo 2: ECC + Kyber Hybrid Key Exchange")
        print("-" * 40)
        demo_ecc_kyber_key_exchange()
        
        # Demo 3: Key Exchange Package
        print("Demo 3: Key Exchange Package")
        print("-" * 40)
        demo_key_exchange_package()
        
        print("🎉 All demos completed successfully!")
        print()
        print("💡 Key Features Demonstrated:")
        print("  • RSA + Kyber hybrid key exchange")
        print("  • ECC + Kyber hybrid key exchange")
        print("  • Session key derivation using SHAKE256")
        print("  • Base64 encoding for transport")
        print("  • Complete package creation")
        print()
        print("🔐 Quantum-Resistant Security:")
        print("  • Classical security from RSA/ECC")
        print("  • Post-quantum security from Kyber")
        print("  • Hybrid approach ensures compatibility")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 