"""
DES Modes of Operation
- ECB (Electronic Codebook)
- CBC (Cipher Block Chaining)
"""

import os
from .des_core import DESCore


class DESModes:
    """DES với các modes of operation"""
    
    def __init__(self):
        self.des_core = DESCore()
        self.block_size = 8  # DES block size = 64 bits = 8 bytes
    
    def _pkcs7_pad(self, data):
        """Padding PKCS#7"""
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
        """Validate key length (8 bytes)"""
        if len(key) != 8:
            raise ValueError(f"DES key must be 8 bytes, got {len(key)}")
        return key
    
    def _validate_iv(self, iv):
        """Validate IV length (8 bytes)"""
        if iv is not None and len(iv) != 8:
            raise ValueError(f"DES IV must be 8 bytes, got {len(iv)}")
        return iv
    
    # ============= ECB MODE =============
    
    def encrypt_ecb(self, plaintext, key):
        """
        Mã hóa DES-ECB
        plaintext: bytes
        key: 8 bytes
        Returns: bytes (ciphertext)
        """
        key = self._validate_key(key)
        
        # Padding
        padded = self._pkcs7_pad(plaintext)
        
        ciphertext = bytearray()
        
        # Mã hóa từng block
        for i in range(0, len(padded), self.block_size):
            block = padded[i:i + self.block_size]
            encrypted_block = self.des_core.encrypt_block(block, key)
            ciphertext.extend(encrypted_block)
        
        return bytes(ciphertext)
    
    def decrypt_ecb(self, ciphertext, key):
        """
        Giải mã DES-ECB
        ciphertext: bytes
        key: 8 bytes
        Returns: bytes (plaintext)
        """
        key = self._validate_key(key)
        
        if len(ciphertext) % self.block_size != 0:
            raise ValueError("Ciphertext length must be multiple of block size")
        
        plaintext = bytearray()
        
        # Giải mã từng block
        for i in range(0, len(ciphertext), self.block_size):
            block = ciphertext[i:i + self.block_size]
            decrypted_block = self.des_core.decrypt_block(block, key)
            plaintext.extend(decrypted_block)
        
        # Remove padding
        return self._pkcs7_unpad(bytes(plaintext))
    
    # ============= CBC MODE =============
    
    def encrypt_cbc(self, plaintext, key, iv=None):
        """
        Mã hóa DES-CBC
        plaintext: bytes
        key: 8 bytes
        iv: 8 bytes (nếu None thì generate random)
        Returns: (ciphertext, iv) tuple
        """
        key = self._validate_key(key)
        
        # Generate IV nếu không có
        if iv is None:
            iv = os.urandom(8)
        else:
            iv = self._validate_iv(iv)
        
        # Padding
        padded = self._pkcs7_pad(plaintext)
        
        ciphertext = bytearray()
        previous_block = iv
        
        # Mã hóa từng block
        for i in range(0, len(padded), self.block_size):
            block = padded[i:i + self.block_size]
            
            # XOR với block trước (hoặc IV)
            xored = bytes(a ^ b for a, b in zip(block, previous_block))
            
            # Encrypt
            encrypted_block = self.des_core.encrypt_block(xored, key)
            ciphertext.extend(encrypted_block)
            
            # Update previous block
            previous_block = encrypted_block
        
        return bytes(ciphertext), iv
    
    def decrypt_cbc(self, ciphertext, key, iv):
        """
        Giải mã DES-CBC
        ciphertext: bytes
        key: 8 bytes
        iv: 8 bytes
        Returns: bytes (plaintext)
        """
        key = self._validate_key(key)
        iv = self._validate_iv(iv)
        
        if len(ciphertext) % self.block_size != 0:
            raise ValueError("Ciphertext length must be multiple of block size")
        
        plaintext = bytearray()
        previous_block = iv
        
        # Giải mã từng block
        for i in range(0, len(ciphertext), self.block_size):
            block = ciphertext[i:i + self.block_size]
            
            # Decrypt
            decrypted_block = self.des_core.decrypt_block(block, key)
            
            # XOR với block trước
            xored = bytes(a ^ b for a, b in zip(decrypted_block, previous_block))
            plaintext.extend(xored)
            
            # Update previous block
            previous_block = block
        
        # Remove padding
        return self._pkcs7_unpad(bytes(plaintext))
    
    # ============= GENERAL INTERFACE =============
    
    def encrypt(self, plaintext, key, mode='ECB', iv=None):
        """
        Mã hóa tổng quát
        mode: 'ECB' hoặc 'CBC'
        Returns: (ciphertext, iv_used) - iv_used là None cho ECB
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
        Giải mã tổng quát
        mode: 'ECB' hoặc 'CBC'
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


def test_des_modes():
    """Test DES modes"""
    des = DESModes()
    
    key = b'TestKey1'  # 8 bytes
    plaintext = b'This is a test message for DES encryption!'
    
    print("="*60)
    print("Testing DES Modes")
    print("="*60)
    
    print(f"\nOriginal plaintext: {plaintext}")
    print(f"Key: {key.hex()}")
    
    # Test ECB
    print("\n" + "-"*60)
    print("ECB Mode:")
    print("-"*60)
    
    ciphertext_ecb, _ = des.encrypt(plaintext, key, mode='ECB')
    print(f"Ciphertext (hex): {ciphertext_ecb.hex()}")
    
    decrypted_ecb = des.decrypt(ciphertext_ecb, key, mode='ECB')
    print(f"Decrypted: {decrypted_ecb}")
    
    if decrypted_ecb == plaintext:
        print("✓ ECB Test passed!")
    else:
        print("✗ ECB Test failed!")
    
    # Test CBC
    print("\n" + "-"*60)
    print("CBC Mode:")
    print("-"*60)
    
    ciphertext_cbc, iv = des.encrypt(plaintext, key, mode='CBC')
    print(f"IV (hex): {iv.hex()}")
    print(f"Ciphertext (hex): {ciphertext_cbc.hex()}")
    
    decrypted_cbc = des.decrypt(ciphertext_cbc, key, mode='CBC', iv=iv)
    print(f"Decrypted: {decrypted_cbc}")
    
    if decrypted_cbc == plaintext:
        print("✓ CBC Test passed!")
    else:
        print("✗ CBC Test failed!")
    
    # So sánh ECB vs CBC
    print("\n" + "-"*60)
    print("Comparing ECB vs CBC:")
    print("-"*60)
    print(f"ECB ciphertext: {ciphertext_ecb.hex()[:60]}...")
    print(f"CBC ciphertext: {ciphertext_cbc.hex()[:60]}...")
    print("Notice: CBC ciphertext is different even with same plaintext!")


if __name__ == "__main__":
    test_des_modes()