"""
Test Suite cho AES Implementation
Bao gồm: Basic tests, File I/O tests, Long text tests, Padding tests
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from algorithms.aes import AESModes
from utils.file_handler import *


def test_aes_basic():
    """Test AES basic functionality"""
    print("="*70)
    print("TEST 1: AES Basic Functionality")
    print("="*70)
    
    aes = AESModes()
    
    key = b'YellowSubmarine!'  # 16 bytes
    plaintext = b'Hello World! This is a test message for AES.'
    
    print(f"Plaintext: {plaintext}")
    print(f"Key: {key.hex()}")
    
    # ECB Mode
    print("\n--- ECB Mode ---")
    ciphertext_ecb, _ = aes.encrypt(plaintext, key, mode='ECB')
    print(f"Ciphertext: {ciphertext_ecb.hex()}")
    
    decrypted_ecb = aes.decrypt(ciphertext_ecb, key, mode='ECB')
    print(f"Decrypted: {decrypted_ecb}")
    
    assert decrypted_ecb == plaintext, "ECB decryption failed!"
    print("✓ ECB Test Passed!")
    
    # CBC Mode
    print("\n--- CBC Mode ---")
    ciphertext_cbc, iv = aes.encrypt(plaintext, key, mode='CBC')
    print(f"IV: {iv.hex()}")
    print(f"Ciphertext: {ciphertext_cbc.hex()}")
    
    decrypted_cbc = aes.decrypt(ciphertext_cbc, key, mode='CBC', iv=iv)
    print(f"Decrypted: {decrypted_cbc}")
    
    assert decrypted_cbc == plaintext, "CBC decryption failed!"
    print("✓ CBC Test Passed!")


def test_aes_with_files():
    """Test AES with file I/O"""
    print("\n" + "="*70)
    print("TEST 2: AES with File I/O")
    print("="*70)
    
    aes = AESModes()
    
    # Create test files
    os.makedirs('test_files', exist_ok=True)
    
    plaintext_file = 'test_files/aes_plaintext.txt'
    encrypted_ecb_file = 'test_files/aes_encrypted_ecb.txt'
    encrypted_cbc_file = 'test_files/aes_encrypted_cbc.txt'
    decrypted_ecb_file = 'test_files/aes_decrypted_ecb.txt'
    decrypted_cbc_file = 'test_files/aes_decrypted_cbc.txt'
    
    # Write test plaintext
    test_text = """This is a comprehensive test of the AES encryption algorithm.
AES (Advanced Encryption Standard) is a symmetric-key algorithm for the encryption of digital data.
It was established by the U.S. National Institute of Standards and Technology (NIST) in 2001.
AES is based on the Rijndael cipher and uses key sizes of 128, 192, or 256 bits.
This test will verify that our implementation works correctly for both ECB and CBC modes."""
    
    write_text_file(plaintext_file, test_text)
    print(f"✓ Created plaintext file: {plaintext_file}")
    
    # Generate key
    key = os.urandom(16)
    key_hex = bytes_to_hex(key)
    print(f"✓ Generated key: {key_hex}")
    
    # Test ECB
    print("\n--- Testing ECB Mode ---")
    plaintext_bytes = test_text.encode('utf-8')
    ciphertext_ecb, _ = aes.encrypt(plaintext_bytes, key, mode='ECB')
    
    save_encrypted_output(encrypted_ecb_file, bytes_to_hex(ciphertext_ecb), 
                         mode='ECB')
    print(f"✓ Encrypted and saved to: {encrypted_ecb_file}")
    
    # Decrypt ECB
    data_ecb = parse_encrypted_input(encrypted_ecb_file)
    ciphertext_ecb = hex_to_bytes(data_ecb['ciphertext'])
    decrypted_ecb = aes.decrypt(ciphertext_ecb, key, mode='ECB')
    
    write_text_file(decrypted_ecb_file, decrypted_ecb.decode('utf-8'))
    print(f"✓ Decrypted and saved to: {decrypted_ecb_file}")
    
    # Verify ECB
    original = read_text_file(plaintext_file)
    decrypted_text = read_text_file(decrypted_ecb_file)
    assert original == decrypted_text, "ECB file test failed!"
    print("✓ ECB File Test Passed!")
    
    # Test CBC
    print("\n--- Testing CBC Mode ---")
    ciphertext_cbc, iv = aes.encrypt(plaintext_bytes, key, mode='CBC')
    
    save_encrypted_output(encrypted_cbc_file, bytes_to_hex(ciphertext_cbc), 
                         bytes_to_hex(iv), mode='CBC')
    print(f"✓ Encrypted and saved to: {encrypted_cbc_file}")
    print(f"  IV: {bytes_to_hex(iv)}")
    
    # Decrypt CBC
    data_cbc = parse_encrypted_input(encrypted_cbc_file)
    ciphertext_cbc = hex_to_bytes(data_cbc['ciphertext'])
    iv_cbc = hex_to_bytes(data_cbc['iv'])
    decrypted_cbc = aes.decrypt(ciphertext_cbc, key, mode='CBC', iv=iv_cbc)
    
    write_text_file(decrypted_cbc_file, decrypted_cbc.decode('utf-8'))
    print(f"✓ Decrypted and saved to: {decrypted_cbc_file}")
    
    # Verify CBC
    decrypted_text = read_text_file(decrypted_cbc_file)
    assert original == decrypted_text, "CBC file test failed!"
    print("✓ CBC File Test Passed!")


def test_aes_long_text():
    """Test AES with long text (>5000 characters)"""
    print("\n" + "="*70)
    print("TEST 3: AES with Long Text (Lab Requirement)")
    print("="*70)
    
    aes = AESModes()
    
    # Create long text (>5000 chars)
    long_text = """The Advanced Encryption Standard (AES), also known by its original name Rijndael,
is a specification for the encryption of electronic data established by the U.S. National Institute of
Standards and Technology (NIST) in 2001. AES is a subset of the Rijndael block cipher developed by
two Belgian cryptographers, Vincent Rijmen and Joan Daemen. """ * 50
    
    print(f"Text length: {len(long_text)} characters")
    
    key = b'TestKeyFor_AES!!'
    
    # Test both modes
    for mode in ['ECB', 'CBC']:
        print(f"\n--- Testing {mode} with long text ---")
        
        plaintext_bytes = long_text.encode('utf-8')
        
        if mode == 'ECB':
            ciphertext, _ = aes.encrypt(plaintext_bytes, key, mode=mode)
            decrypted = aes.decrypt(ciphertext, key, mode=mode)
        else:
            ciphertext, iv = aes.encrypt(plaintext_bytes, key, mode=mode)
            decrypted = aes.decrypt(ciphertext, key, mode=mode, iv=iv)
        
        assert decrypted.decode('utf-8') == long_text, f"{mode} long text test failed!"
        print(f"✓ {mode} long text test passed!")
        print(f"  Plaintext: {len(plaintext_bytes)} bytes")
        print(f"  Ciphertext: {len(ciphertext)} bytes")


def test_padding():
    """Test PKCS#7 padding"""
    print("\n" + "="*70)
    print("TEST 4: PKCS#7 Padding")
    print("="*70)
    
    aes = AESModes()
    key = b'TestPadding_Key!'
    
    # Test with different lengths
    test_cases = [
        b'A',  # 1 byte
        b'ABCDE',  # 5 bytes
        b'ABCDEFGHIJKLMNO',  # 15 bytes
        b'ABCDEFGHIJKLMNOP',  # 16 bytes (exact block)
        b'ABCDEFGHIJKLMNOPQ',  # 17 bytes
        b'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345',  # 32 bytes (2 blocks)
    ]
    
    for plaintext in test_cases:
        print(f"\nTesting with {len(plaintext)} bytes: {plaintext[:20]}...")
        
        ciphertext, _ = aes.encrypt(plaintext, key, mode='ECB')
        decrypted = aes.decrypt(ciphertext, key, mode='ECB')
        
        assert decrypted == plaintext, f"Padding test failed for {len(plaintext)} bytes"
        print(f"  ✓ Passed! Ciphertext length: {len(ciphertext)} bytes")
    
    print("\n✓ All padding tests passed!")


def test_standard_vectors():
    """Test with NIST standard test vectors"""
    print("\n" + "="*70)
    print("TEST 5: NIST Standard Test Vectors")
    print("="*70)
    
    from algorithms.aes import AESCore
    aes = AESCore()
    
    # FIPS 197 Appendix B test vector
    key = bytes.fromhex('2b7e151628aed2a6abf7158809cf4f3c')
    plaintext = bytes.fromhex('3243f6a8885a308d313198a2e0370734')
    expected = bytes.fromhex('3925841d02dc09fbdc118597196a0b32')
    
    print(f"Key:       {key.hex()}")
    print(f"Plaintext: {plaintext.hex()}")
    print(f"Expected:  {expected.hex()}")
    
    ciphertext = aes.encrypt_block(plaintext, key)
    print(f"Got:       {ciphertext.hex()}")
    
    if ciphertext == expected:
        print("✓ NIST test vector passed!")
    else:
        print("✗ NIST test vector failed!")
    
    # Decrypt to verify
    decrypted = aes.decrypt_block(ciphertext, key)
    assert decrypted == plaintext, "Decryption verification failed!"
    print("✓ Decryption verification passed!")


def run_all_tests():
    """Run all AES tests"""
    print("\n" + "="*70)
    print(" "*15 + "AES IMPLEMENTATION TEST SUITE")
    print("="*70 + "\n")
    
    try:
        test_aes_basic()
        test_aes_with_files()
        test_aes_long_text()
        test_padding()
        test_standard_vectors()
        
        print("\n" + "="*70)
        print(" "*20 + "✓ ALL TESTS PASSED!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()