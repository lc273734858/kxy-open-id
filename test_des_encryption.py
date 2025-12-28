#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for DES encryption implementation
"""

from app.utils.auth_utils import DesEncryption, encrypt_password, decrypt_password


def test_des_encryption():
    """Test DES encryption and decryption"""
    print("=" * 60)
    print("Testing DES Encryption Implementation")
    print("=" * 60)

    # Test 1: Basic encryption/decryption
    print("\n[Test 1] Basic Encryption/Decryption")
    original_password = "myPassword123"
    print(f"Original password: {original_password}")

    encrypted = encrypt_password(original_password)
    print(f"Encrypted (hex): {encrypted}")

    decrypted = decrypt_password(encrypted)
    print(f"Decrypted: {decrypted}")

    assert original_password == decrypted, "Decryption failed!"
    print("✓ Test 1 passed")

    # Test 2: Using class instance directly
    print("\n[Test 2] Using DesEncryption Class")
    crypto = DesEncryption()
    test_string = "Hello, 驿氪!"
    print(f"Original: {test_string}")

    encrypted2 = crypto.encrypt(test_string)
    print(f"Encrypted: {encrypted2}")

    decrypted2 = crypto.decrypt(encrypted2)
    print(f"Decrypted: {decrypted2}")

    assert test_string == decrypted2, "Class-based encryption failed!"
    print("✓ Test 2 passed")

    # Test 3: Custom key
    print("\n[Test 3] Custom Key")
    custom_key = "12345678"  # 8 bytes
    crypto_custom = DesEncryption(key=custom_key)
    test_password = "admin@123"
    print(f"Original: {test_password}")
    print(f"Custom key: {custom_key}")

    encrypted3 = crypto_custom.encrypt(test_password)
    print(f"Encrypted: {encrypted3}")

    decrypted3 = crypto_custom.decrypt(encrypted3)
    print(f"Decrypted: {decrypted3}")

    assert test_password == decrypted3, "Custom key encryption failed!"
    print("✓ Test 3 passed")

    # Test 4: Multiple passwords
    print("\n[Test 4] Multiple Passwords")
    passwords = ["admin", "user123", "P@ssw0rd!", "测试密码"]
    for pwd in passwords:
        enc = encrypt_password(pwd)
        dec = decrypt_password(enc)
        print(f"{pwd:20} -> {enc:40} -> {dec}")
        assert pwd == dec, f"Failed for password: {pwd}"
    print("✓ Test 4 passed")

    print("\n" + "=" * 60)
    print("All tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_des_encryption()
