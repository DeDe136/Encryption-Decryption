"""
Script để test các thuật toán mã hóa
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from algorithms.caesar.caesar_cipher import CaesarCipher
from algorithms.monoalphabetic.mono_cipher import MonoalphabeticCipher
from algorithms.vigenere.vigenere_cipher import VigenereCipher

def test_caesar():
    """Test Caesar Cipher"""
    print("="*60)
    print("TESTING CAESAR CIPHER")
    print("="*60)
    
    cipher = CaesarCipher()
    
    # Test text
    plaintext = """The quick brown fox jumps over the lazy dog. This is a test 
    of the Caesar cipher algorithm. It should be able to crack this easily."""
    
    # Encrypt with key = 7
    key = 7
    print(f"Original plaintext: {plaintext[:100]}...")
    print(f"\nEncrypting with key = {key}")
    
    # Encrypt (using decrypt with negative key)
    ciphertext = cipher.decrypt_with_key(plaintext, -key)
    print(f"Ciphertext: {ciphertext[:100]}...")
    
    # Crack
    print("\n" + "="*60)
    print("CRACKING...")
    print("="*60)
    
    found_key, decrypted = cipher.crack(ciphertext)
    
    print(f"\n\nFOUND KEY: {found_key}")
    print(f"EXPECTED KEY: {key}")
    print(f"MATCH: {'✓' if found_key == key else '✗'}")
    print(f"\nDecrypted: {decrypted[:100]}...")
    
    return found_key == key

def test_vigenere():
    """Test Vigenère Cipher"""
    print("\n\n" + "="*60)
    print("TESTING VIGENÈRE CIPHER")
    print("="*60)
    
    cipher = VigenereCipher()
    
    # Test text (repeated to make it longer)
    plaintext = """The Vigenere cipher is a method of encrypting alphabetic text 
    by using a series of interwoven Caesar ciphers based on the letters of a keyword. 
    It is a form of polyalphabetic substitution.""" * 10
    
    key = "SECRET"
    print(f"Original plaintext length: {len(plaintext)}")
    print(f"Encryption key: '{key}'")
    
    # Encrypt
    ciphertext_chars = []
    key_index = 0
    for char in plaintext:
        if char.isalpha():
            is_upper = char.isupper()
            char = char.lower()
            shift = ord(key[key_index % len(key)]) - ord('a')
            encrypted_char = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            if is_upper:
                encrypted_char = encrypted_char.upper()
            ciphertext_chars.append(encrypted_char)
            key_index += 1
        else:
            ciphertext_chars.append(char)
    
    ciphertext = ''.join(ciphertext_chars)
    print(f"Ciphertext preview: {ciphertext[:100]}...")
    
    # Crack
    print("\n" + "="*60)
    print("CRACKING...")
    print("="*60)
    
    found_key, decrypted = cipher.crack(ciphertext)
    
    print(f"\n\nFOUND KEY: {found_key}")
    print(f"EXPECTED KEY: {key}")
    print(f"MATCH: {'✓' if found_key.upper() == key.upper() else '✗'}")
    print(f"\nDecrypted preview: {decrypted[:100]}...")
    
    return found_key.upper() == key.upper()

def create_test_files():
    """Tạo file test mẫu"""
    print("\n\n" + "="*60)
    print("CREATING TEST FILES")
    print("="*60)
    
    # Create test directory
    test_dir = "test_files"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print(f"✓ Created directory: {test_dir}")
    
    # Caesar test file
    caesar_plain = """The quick brown fox jumps over the lazy dog. This is a longer test 
    of the Caesar cipher algorithm. We need more text to make the frequency analysis work better.
    The Caesar cipher is one of the simplest and most widely known encryption techniques. 
    It is a type of substitution cipher in which each letter in the plaintext is replaced by a 
    letter some fixed number of positions down the alphabet.""" * 10
    
    cipher = CaesarCipher()
    caesar_cipher = cipher.decrypt_with_key(caesar_plain, -13)  # key = 13
    
    with open(f"{test_dir}/caesar_test.txt", "w", encoding="utf-8") as f:
        f.write(caesar_cipher)
    print(f"✓ Created: {test_dir}/caesar_test.txt (key=13)")
    
    # Vigenère test file
    vigenere_plain = """The Vigenere cipher is a method of encrypting alphabetic text by using 
    a series of interwoven Caesar ciphers based on the letters of a keyword. It is a form of 
    polyalphabetic substitution. The Vigenere cipher has been reinvented many times. The method 
    was originally described by Giovan Battista Bellaso in his book. However the scheme was later 
    misattributed to Blaise de Vigenere in the nineteenth century and is now widely known as the 
    Vigenere cipher.""" * 20
    
    key = "LEMON"
    vigenere_cipher_chars = []
    key_index = 0
    for char in vigenere_plain:
        if char.isalpha():
            is_upper = char.isupper()
            char = char.lower()
            shift = ord(key[key_index % len(key)]) - ord('A')
            encrypted_char = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            if is_upper:
                encrypted_char = encrypted_char.upper()
            vigenere_cipher_chars.append(encrypted_char)
            key_index += 1
        else:
            vigenere_cipher_chars.append(char)
    
    vigenere_cipher = ''.join(vigenere_cipher_chars)
    
    with open(f"{test_dir}/vigenere_test.txt", "w", encoding="utf-8") as f:
        f.write(vigenere_cipher)
    print(f"✓ Created: {test_dir}/vigenere_test.txt (key=LEMON)")
    
    print(f"\n✓ Test files created in '{test_dir}/' directory")
    print(f"  You can use these files to test the UI application")

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("LAB 06 - ALGORITHM TESTS")
    print("="*60 + "\n")
    
    # Test Caesar
    try:
        caesar_result = test_caesar()
        print(f"\n{'✓' if caesar_result else '✗'} Caesar Cipher Test")
    except Exception as e:
        print(f"\n✗ Caesar Cipher Test Failed: {e}")
    
    # Test Vigenère
    try:
        vigenere_result = test_vigenere()
        print(f"\n{'✓' if vigenere_result else '✗'} Vigenère Cipher Test")
    except Exception as e:
        print(f"\n✗ Vigenère Cipher Test Failed: {e}")
    
    # Create test files
    create_test_files()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)

if __name__ == "__main__":
    main()