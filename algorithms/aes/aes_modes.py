"""
AES Modes of Operation
- ECB (Electronic Codebook)
- CBC (Cipher Block Chaining)
"""

import os
from .aes_core import AESCore


class AESModes:
    """AES with ECB and CBC modes"""
    
    def __init__(self):
        self.aes_core = AESCore()
        self.block_size = 16  # AES block size = 128 bits = 16 bytes
    
    def _pkcs7_pad(self, data):
        """
        PKCS#7 Padding
        Pad data to multiple of block_size
        """
        pad_len = self.block_size - (len(data) % self.block_size)
        padding = bytes([pad_len] * pad_len)
        return data + padding
    
    def _pkcs7_unpad(self, data):
        """Remove PKCS#7 padding"""
        if not data:
            return data
        
        pad_len = data[-1]
        
        # Validate padding
        if pad_len > self.block_size or pad_len == 0:
            raise ValueError("Invalid padding")
        
        # Check if all padding bytes are correct
        if data[-pad_len:] != bytes([pad_len] * pad_len):
            raise ValueError("Invalid padding")
        
        return data[:-pad_len]
    
    def _validate_key(self, key):
        """Validate AES key length"""
        if len(key) != 16:
            raise ValueError(f"AES-128 key must be 16 bytes, got {len(key)}")
        return key
    
    def _validate_iv(self, iv):
        """Validate IV length"""
        if iv is not None and len(iv) != 16:
            raise ValueError(f"AES IV must be 16 bytes, got {len(iv)}")
        return iv
    
    # ==================== ECB MODE ====================
    
    def encrypt_ecb(self, plaintext, key):
        """
        AES-ECB Encryption
        plaintext: bytes
        key: 16 bytes
        Returns: bytes (ciphertext)
        """
        key = self._validate_key(key)
        
        # Padding
        padded = self._pkcs7_pad(plaintext)
        
        ciphertext = bytearray()
        
        # Encrypt each block
        for i in range(0, len(padded), self.block_size):
            block = padded[i:i + self.block_size]
            encrypted_block = self.aes_core.encrypt_block(block, key)
            ciphertext.extend(encrypted_block)
        
        return bytes(ciphertext)
    
    def decrypt_ecb(self, ciphertext, key):
        """
        AES-ECB Decryption
        ciphertext: bytes
        key: 16 bytes
        Returns: bytes (plaintext)
        """
        key = self._validate_key(key)
        
        if len(ciphertext) % self.block_size != 0:
            raise ValueError("Ciphertext length must be multiple of block size")
        
        plaintext = bytearray()
        
        # Decrypt each block
        for i in range(0, len(ciphertext), self.block_size):
            block = ciphertext[i:i + self.block_size]
            decrypted_block = self.aes_core.decrypt_block(block, key)
            plaintext.extend(decrypted_block)
        
        # Remove padding
        return self._pkcs7_unpad(bytes(plaintext))
    
    # ==================== CBC MODE ====================
    
    def encrypt_cbc(self, plaintext, key, iv=None):
        """
        AES-CBC Encryption
        plaintext: bytes
        key: 16 bytes
        iv: 16 bytes (if None, generate random)
        Returns: (ciphertext, iv) tuple
        """
        key = self._validate_key(key)
        
        # Generate IV if not provided
        if iv is None:
            iv = os.urandom(16)
        else:
            iv = self._validate_iv(iv)
        
        # Padding
        padded = self._pkcs7_pad(plaintext)
        
        ciphertext = bytearray()
        previous_block = iv
        
        # Encrypt each block
        for i in range(0, len(padded), self.block_size):
            block = padded[i:i + self.block_size]
            
            # XOR with previous block (or IV)
            xored = bytes(a ^ b for a, b in zip(block, previous_block))
            
            # Encrypt
            encrypted_block = self.aes_core.encrypt_block(xored, key)
            ciphertext.extend(encrypted_block)
            
            # Update previous block
            previous_block = encrypted_block
        
        return bytes(ciphertext), iv
    
    def decrypt_cbc(self, ciphertext, key, iv):
        """
        AES-CBC Decryption
        ciphertext: bytes
        key: 16 bytes
        iv: 16 bytes
        Returns: bytes (plaintext)
        """
        key = self._validate_key(key)
        iv = self._validate_iv(iv)
        
        if len(ciphertext) % self.block_size != 0:
            raise ValueError("Ciphertext length must be multiple of block size")
        
        plaintext = bytearray()
        previous_block = iv
        
        # Decrypt each block
        for i in range(0, len(ciphertext), self.block_size):
            block = ciphertext[i:i + self.block_size]
            
            # Decrypt
            decrypted_block = self.aes_core.decrypt_block(block, key)
            
            # XOR with previous block
            xored = bytes(a ^ b for a, b in zip(decrypted_block, previous_block))
            plaintext.extend(xored)
            
            # Update previous block
            previous_block = block
        
        # Remove padding
        return self._pkcs7_unpad(bytes(plaintext))
    
    # ==================== GENERAL INTERFACE ====================
    
    def encrypt(self, plaintext, key, mode='ECB', iv=None):
        """
        General encryption interface
        mode: 'ECB' or 'CBC'
        Returns: (ciphertext, iv_used) - iv_used is None for ECB
        """
        mode = mode.upper()
        
        if mode == 'ECB':
            ciphertext = self.encrypt_ecb(plaintext, key)
            return ciphertext, None
        
        elif mode == 'CBC':
            ciphertext, iv_used = self.encrypt_cbc(plaintext, key, iv)
            return ciphertext, iv_used
        
        else:
            raise ValueError(f"Unsupported mode: {mode}")
    
    def decrypt(self, ciphertext, key, mode='ECB', iv=None):
        """
        General decryption interface
        mode: 'ECB' or 'CBC'
        iv: Required for CBC, ignored for ECB
        Returns: plaintext
        """
        mode = mode.upper()
        
        if mode == 'ECB':
            return self.decrypt_ecb(ciphertext, key)
        
        elif mode == 'CBC':
            if iv is None:
                raise ValueError("IV is required for CBC mode")
            return self.decrypt_cbc(ciphertext, key, iv)
        
        else:
            raise ValueError(f"Unsupported mode: {mode}")


def test_aes_modes():
    """Test AES modes"""
    aes = AESModes()
    
    key = b'YellowSubmarine!'  # 16 bytes
    plaintext = b'This is a comprehensive test of AES encryption with multiple blocks!'
    
    print("="*70)
    print("TESTING AES MODES")
    print("="*70)
    
    print(f"\nOriginal plaintext: {plaintext}")
    print(f"Key: {key.hex()}")
    print(f"Plaintext length: {len(plaintext)} bytes")
    
    # Test ECB
    print("\n" + "-"*70)
    print("ECB Mode:")
    print("-"*70)
    
    ciphertext_ecb, _ = aes.encrypt(plaintext, key, mode='ECB')
    print(f"Ciphertext (hex): {ciphertext_ecb.hex()}")
    print(f"Ciphertext length: {len(ciphertext_ecb)} bytes")
    
    decrypted_ecb = aes.decrypt(ciphertext_ecb, key, mode='ECB')
    print(f"Decrypted: {decrypted_ecb}")
    
    if decrypted_ecb == plaintext:
        print("✓ ECB Test passed!")
    else:
        print("✗ ECB Test failed!")
    
    # Test CBC
    print("\n" + "-"*70)
    print("CBC Mode:")
    print("-"*70)
    
    ciphertext_cbc, iv = aes.encrypt(plaintext, key, mode='CBC')
    print(f"IV (hex): {iv.hex()}")
    print(f"Ciphertext (hex): {ciphertext_cbc.hex()}")
    print(f"Ciphertext length: {len(ciphertext_cbc)} bytes")
    
    decrypted_cbc = aes.decrypt(ciphertext_cbc, key, mode='CBC', iv=iv)
    print(f"Decrypted: {decrypted_cbc}")
    
    if decrypted_cbc == plaintext:
        print("✓ CBC Test passed!")
    else:
        print("✗ CBC Test failed!")
    
    # Compare ECB vs CBC
    print("\n" + "-"*70)
    print("Comparing ECB vs CBC:")
    print("-"*70)
    print(f"ECB ciphertext: {ciphertext_ecb.hex()[:80]}...")
    print(f"CBC ciphertext: {ciphertext_cbc.hex()[:80]}...")
    print("Notice: CBC ciphertext differs due to IV and chaining!")
    
    print("\n" + "="*70)
    print("ALL AES MODE TESTS COMPLETED")
    print("="*70)


if __name__ == "__main__":
    test_aes_modes()