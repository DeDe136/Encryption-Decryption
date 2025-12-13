
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from algorithms.des import DESModes
from utils.file_handler import *


def test_des_basic():
    """Test DES basic encryption/decryption"""
    print("="*60)
    print("TEST 1: DES Basic Functionality")
    print("="*60)
    
    des = DESModes()
    
    key = b'TestKey1'  # 8 bytes
    plaintext = b'Hello World! This is a test message.'
    
    print(f"Plaintext: {plaintext}")
    print(f"Key: {key.hex()}")
    
    # ECB Mode
    print("\n--- ECB Mode ---")
    ciphertext_ecb, _ = des.encrypt(plaintext, key, mode='ECB')
    print(f"Ciphertext: {ciphertext_ecb.hex()}")
    
    decrypted_ecb = des.decrypt(ciphertext_ecb, key, mode='ECB')
    print(f"Decrypted: {decrypted_ecb}")
    
    assert decrypted_ecb == plaintext, "ECB decryption failed!"
    print("✓ ECB Test Passed!")
    
    # CBC Mode
    print("\n--- CBC Mode ---")
    ciphertext_cbc, iv = des.encrypt(plaintext, key, mode='CBC')
    print(f"IV: {iv.hex()}")
    print(f"Ciphertext: {ciphertext_cbc.hex()}")
    
    decrypted_cbc = des.decrypt(ciphertext_cbc, key, mode='CBC', iv=iv)
    print(f"Decrypted: {decrypted_cbc}")
    
    assert decrypted_cbc == plaintext, "CBC decryption failed!"
    print("✓ CBC Test Passed!")


def test_des_with_files():
    """Test DES với file I/O"""
    print("\n" + "="*60)
    print("TEST 2: DES with File I/O")
    print("="*60)
    
    des = DESModes()
    
    # Create test files
    os.makedirs('test_files', exist_ok=True)
    
    plaintext_file = 'test_files/des_plaintext.txt'
    encrypted_ecb_file = 'test_files/des_encrypted_ecb.txt'
    encrypted_cbc_file = 'test_files/des_encrypted_cbc.txt'
    decrypted_ecb_file = 'test_files/des_decrypted_ecb.txt'
    decrypted_cbc_file = 'test_files/des_decrypted_cbc.txt'
    
    # Write test plaintext
    test_text = """This is a comprehensive test of the DES encryption algorithm.
DES (Data Encryption Standard) is a symmetric-key algorithm for the encryption of digital data.
Although its short key length of 56 bits makes it too insecure for modern applications,
it was highly influential in the advancement of cryptography.
This test will verify that our implementation works correctly for both ECB and CBC modes."""
    
    write_text_file(plaintext_file, test_text)
    print(f"✓ Created plaintext file: {plaintext_file}")
    
    # Generate key
    key = os.urandom(8)
    key_hex = bytes_to_hex(key)
    print(f"✓ Generated key: {key_hex}")
    
    # Test ECB
    print("\n--- Testing ECB Mode ---")
    plaintext_bytes = test_text.encode('utf-8')
    ciphertext_ecb, _ = des.encrypt(plaintext_bytes, key, mode='ECB')
    
    save_encrypted_output(encrypted_ecb_file, bytes_to_hex(ciphertext_ecb), 
                         mode='ECB')
    print(f"✓ Encrypted and saved to: {encrypted_ecb_file}")
    
    # Decrypt ECB
    data_ecb = parse_encrypted_input(encrypted_ecb_file)
    ciphertext_ecb = hex_to_bytes(data_ecb['ciphertext'])
    decrypted_ecb = des.decrypt(ciphertext_ecb, key, mode='ECB')
    
    write_text_file(decrypted_ecb_file, decrypted_ecb.decode('utf-8'))
    print(f"✓ Decrypted and saved to: {decrypted_ecb_file}")
    
    # Verify ECB
    original = read_text_file(plaintext_file)
    decrypted_text = read_text_file(decrypted_ecb_file)
    assert original == decrypted_text, "ECB file test failed!"
    print("✓ ECB File Test Passed!")
    
    # Test CBC
    print("\n--- Testing CBC Mode ---")
    ciphertext_cbc, iv = des.encrypt(plaintext_bytes, key, mode='CBC')
    
    save_encrypted_output(encrypted_cbc_file, bytes_to_hex(ciphertext_cbc), 
                         bytes_to_hex(iv), mode='CBC')
    print(f"✓ Encrypted and saved to: {encrypted_cbc_file}")
    print(f"  IV: {bytes_to_hex(iv)}")
    
    # Decrypt CBC
    data_cbc = parse_encrypted_input(encrypted_cbc_file)
    ciphertext_cbc = hex_to_bytes(data_cbc['ciphertext'])
    iv_cbc = hex_to_bytes(data_cbc['iv'])
    decrypted_cbc = des.decrypt(ciphertext_cbc, key, mode='CBC', iv=iv_cbc)
    
    write_text_file(decrypted_cbc_file, decrypted_cbc.decode('utf-8'))
    print(f"✓ Decrypted and saved to: {decrypted_cbc_file}")
    
    # Verify CBC
    decrypted_text = read_text_file(decrypted_cbc_file)
    assert original == decrypted_text, "CBC file test failed!"
    print("✓ CBC File Test Passed!")


def test_des_long_text():
    """Test DES với văn bản dài (>5000 characters)"""
    print("\n" + "="*60)
    print("TEST 3: DES with Long Text (Lab Requirement)")
    print("="*60)
    
    des = DESModes()
    
    # Create long text (>5000 chars)
    long_text = """The Data Encryption Standard (DES) is a symmetric-key algorithm 
for the encryption of digital data. Although its short key length of 56 bits makes 
it too insecure for most modern applications, it was highly influential in the 
advancement of modern cryptography. """ * 100  # Repeat to make it long
    
    print(f"Text length: {len(long_text)} characters")
    
    key = b'LongTest'
    
    # Test both modes
    for mode in ['ECB', 'CBC']:
        print(f"\n--- Testing {mode} with long text ---")
        
        plaintext_bytes = long_text.encode('utf-8')
        
        if mode == 'ECB':
            ciphertext, _ = des.encrypt(plaintext_bytes, key, mode=mode)
            decrypted = des.decrypt(ciphertext, key, mode=mode)
        else:
            ciphertext, iv = des.encrypt(plaintext_bytes, key, mode=mode)
            decrypted = des.decrypt(ciphertext, key, mode=mode, iv=iv)
        
        assert decrypted.decode('utf-8') == long_text, f"{mode} long text test failed!"
        print(f"✓ {mode} long text test passed!")


def test_padding():
    """Test PKCS#7 padding"""
    print("\n" + "="*60)
    print("TEST 4: PKCS#7 Padding")
    print("="*60)
    
    des = DESModes()
    key = b'PadTest1'
    
    # Test với các độ dài khác nhau
    test_cases = [
        b'1',  # 1 byte
        b'12345',  # 5 bytes
        b'1234567',  # 7 bytes
        b'12345678',  # 8 bytes (exact block)
        b'123456789',  # 9 bytes
        b'1234567890123456',  # 16 bytes (2 blocks)
    ]
    
    for plaintext in test_cases:
        print(f"\nTesting with {len(plaintext)} bytes: {plaintext}")
        
        ciphertext, _ = des.encrypt(plaintext, key, mode='ECB')
        decrypted = des.decrypt(ciphertext, key, mode='ECB')
        
        assert decrypted == plaintext, f"Padding test failed for {len(plaintext)} bytes"
        print(f"  ✓ Passed! Ciphertext length: {len(ciphertext)} bytes")
    
    print("\n✓ All padding tests passed!")


def run_all_tests():
    """Run tất cả các tests"""
    print("\n" + "="*70)
    print(" "*15 + "DES IMPLEMENTATION TEST SUITE")
    print("="*70 + "\n")
    
    try:
        test_des_basic()
        test_des_with_files()
        test_des_long_text()
        test_padding()
        
        print("\n" + "="*70)
        print(" "*20 + "✓ ALL TESTS PASSED!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()