#!/usr/bin/env python3
"""
Off-chain script to encrypt API key for on-chain storage.

This script demonstrates how to encrypt an API key before storing it
in a GenLayer contract that uses the Encrypted On-chain Pattern.

Usage:
    python scripts/encrypt_key.py "your-api-key-here"

Output:
    Prints the encrypted (base64-encoded) key that can be stored on-chain.
    Also prints the decryption key (store securely on leader nodes).
"""

import sys
import base64
from typing import Optional

try:
    from cryptography.fernet import Fernet
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    print("⚠️  Warning: cryptography library not installed.")
    print("   Install with: pip install cryptography")
    print("   Falling back to base64 encoding (NOT SECURE for production)\n")


def encrypt_with_fernet(api_key: str, encryption_key: Optional[bytes] = None) -> tuple[str, str]:
    """
    Encrypt API key using Fernet (symmetric encryption).
    
    Args:
        api_key: The API key to encrypt
        encryption_key: Optional encryption key (generates new if None)
    
    Returns:
        Tuple of (encrypted_key_b64, encryption_key_b64)
    """
    if encryption_key is None:
        encryption_key = Fernet.generate_key()
    
    cipher = Fernet(encryption_key)
    encrypted = cipher.encrypt(api_key.encode('utf-8'))
    encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
    
    return encrypted_b64, encryption_key.decode('utf-8')


def encrypt_simple(api_key: str) -> str:
    """
    Simple base64 encoding (NOT SECURE - for demo only).
    
    In production, always use proper encryption.
    """
    encoded = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')
    return encoded


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python encrypt_key.py <api-key>")
        print("\nExample:")
        print("  python encrypt_key.py 'your-api-key-here'")
        sys.exit(1)
    
    api_key = sys.argv[1]
    
    if not api_key or api_key.strip() == "":
        print("Error: API key cannot be empty")
        sys.exit(1)
    
    print(f"Encrypting API key: {api_key[:10]}...{api_key[-4:]} (hidden)\n")
    
    if HAS_CRYPTOGRAPHY:
        # Use proper encryption
        encrypted_b64, encryption_key_b64 = encrypt_with_fernet(api_key)
        
        print("✅ Encrypted using Fernet (AES-128-CBC)")
        print("\n📋 Encrypted Key (use this in contract.set_api_key()):")
        print("-" * 70)
        print(encrypted_b64)
        print("-" * 70)
        print("\n🔑 Decryption Key (store securely on leader nodes only!):")
        print("-" * 70)
        print(encryption_key_b64)
        print("-" * 70)
        print("\n⚠️  SECURITY NOTES:")
        print("   1. Store decryption key securely (environment variables, secrets manager)")
        print("   2. Only leader nodes should have access to decryption key")
        print("   3. Rotate encryption keys periodically")
        print("   4. Never commit decryption keys to version control")
    else:
        # Fallback to simple encoding
        encrypted_b64 = encrypt_simple(api_key)
        
        print("⚠️  Using base64 encoding (NOT SECURE for production)")
        print("\n📋 Encoded Key (use this in contract.set_api_key()):")
        print("-" * 70)
        print(encrypted_b64)
        print("-" * 70)
        print("\n⚠️  WARNING:")
        print("   This is NOT secure encryption!")
        print("   Install cryptography library for proper encryption:")
        print("   pip install cryptography")
    
    print("\n✅ Done! Copy the encrypted key and use it in your contract.")


if __name__ == '__main__':
    main()

