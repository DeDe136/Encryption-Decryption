

# Initial Permutation (IP) Table
IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]

# Final Permutation (IP^-1) Table
IP_INV = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25
]

# Expansion Table (E)
E = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]

# Permutation Function (P)
P = [
    16, 7, 20, 21, 29, 12, 28, 17,
    1, 15, 23, 26, 5, 18, 31, 10,
    2, 8, 24, 14, 32, 27, 3, 9,
    19, 13, 30, 6, 22, 11, 4, 25
]

# S-Boxes (8 S-boxes, mỗi cái 4x16)
S_BOXES = [
    # S1
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
    ],
    # S2
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
    ],
    # S3
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
    ],
    # S4
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
    ],
    # S5
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
    ],
    # S6
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
    ],
    # S7
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
    ],
    # S8
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
    ]
]

# Permuted Choice 1 (PC-1) - Key schedule
PC1 = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4
]

# Permuted Choice 2 (PC-2) - Key schedule
PC2 = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

# Left shifts for key schedule
SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]


class DESCore:
    """DES Core Algorithm - mã hóa/giải mã 1 block 64-bit"""
    
    def __init__(self):
        pass
    
    def _permute(self, block, table):
        """Áp dụng permutation table lên block"""
        return [block[i - 1] for i in table]
    
    def _xor(self, bits1, bits2):
        """XOR hai chuỗi bit"""
        return [b1 ^ b2 for b1, b2 in zip(bits1, bits2)]
    
    def _left_shift(self, bits, n):
        """Dịch trái vòng n bits"""
        return bits[n:] + bits[:n]
    
    def _bytes_to_bits(self, data):
        """Chuyển bytes thành list of bits"""
        bits = []
        for byte in data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        return bits
    
    def _bits_to_bytes(self, bits):
        """Chuyển list of bits thành bytes"""
        result = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte = (byte << 1) | bits[i + j]
            result.append(byte)
        return bytes(result)
    
    def _generate_subkeys(self, key_bits):
        """Tạo 16 subkeys từ key 64-bit"""
        # PC-1: 64 bits -> 56 bits
        key_56 = self._permute(key_bits, PC1)
        
        # Chia thành 2 nửa
        C = key_56[:28]
        D = key_56[28:]
        
        subkeys = []
        
        for i in range(16):
            # Left shift
            C = self._left_shift(C, SHIFTS[i])
            D = self._left_shift(D, SHIFTS[i])
            
            # Combine và PC-2: 56 bits -> 48 bits
            CD = C + D
            subkey = self._permute(CD, PC2)
            subkeys.append(subkey)
        
        return subkeys
    
    def _s_box_substitution(self, expanded_bits):
        """Áp dụng 8 S-boxes"""
        output = []
        
        for i in range(8):
            # Lấy 6 bits
            chunk = expanded_bits[i * 6:(i + 1) * 6]
            
            # Row: bit đầu và cuối
            row = (chunk[0] << 1) | chunk[5]
            
            # Column: 4 bits giữa
            col = (chunk[1] << 3) | (chunk[2] << 2) | (chunk[3] << 1) | chunk[4]
            
            # Lấy giá trị từ S-box
            val = S_BOXES[i][row][col]
            
            # Chuyển thành 4 bits
            for j in range(3, -1, -1):
                output.append((val >> j) & 1)
        
        return output
    
    def _f_function(self, right_half, subkey):
        """Hàm F của DES"""
        # Expansion: 32 bits -> 48 bits
        expanded = self._permute(right_half, E)
        
        # XOR với subkey
        xored = self._xor(expanded, subkey)
        
        # S-box substitution: 48 bits -> 32 bits
        substituted = self._s_box_substitution(xored)
        
        # Permutation P
        result = self._permute(substituted, P)
        
        return result
    
    def _des_round(self, left, right, subkey):
        """Một round của DES"""
        # New right = left XOR f(right, subkey)
        new_right = self._xor(left, self._f_function(right, subkey))
        
        # New left = old right
        new_left = right
        
        return new_left, new_right
    
    def encrypt_block(self, plaintext_block, key):
        """
        Mã hóa 1 block 64-bit
        plaintext_block: 8 bytes
        key: 8 bytes
        Returns: 8 bytes
        """
        # Chuyển thành bits
        plain_bits = self._bytes_to_bits(plaintext_block)
        key_bits = self._bytes_to_bits(key)
        
        # Initial permutation
        permuted = self._permute(plain_bits, IP)
        
        # Chia thành 2 nửa
        left = permuted[:32]
        right = permuted[32:]
        
        # Generate subkeys
        subkeys = self._generate_subkeys(key_bits)
        
        # 16 rounds
        for i in range(16):
            left, right = self._des_round(left, right, subkeys[i])
        
        # Swap cuối cùng
        combined = right + left
        
        # Final permutation
        ciphertext_bits = self._permute(combined, IP_INV)
        
        # Chuyển về bytes
        return self._bits_to_bytes(ciphertext_bits)
    
    def decrypt_block(self, ciphertext_block, key):
        """
        Giải mã 1 block 64-bit
        Giống encrypt nhưng dùng subkeys theo thứ tự ngược lại
        """
        # Chuyển thành bits
        cipher_bits = self._bytes_to_bits(ciphertext_block)
        key_bits = self._bytes_to_bits(key)
        
        # Initial permutation
        permuted = self._permute(cipher_bits, IP)
        
        # Chia thành 2 nửa
        left = permuted[:32]
        right = permuted[32:]
        
        # Generate subkeys
        subkeys = self._generate_subkeys(key_bits)
        
        # 16 rounds với subkeys ngược
        for i in range(15, -1, -1):
            left, right = self._des_round(left, right, subkeys[i])
        
        # Swap cuối cùng
        combined = right + left
        
        # Final permutation
        plaintext_bits = self._permute(combined, IP_INV)
        
        # Chuyển về bytes
        return self._bits_to_bytes(plaintext_bits)


def test_des_core():
    """Test DES core"""
    des = DESCore()
    
    # Test với key và plaintext đơn giản
    key = b'12345678'  # 8 bytes
    plaintext = b'ABCDEFGH'  # 8 bytes
    
    print("Testing DES Core...")
    print(f"Key: {key.hex()}")
    print(f"Plaintext: {plaintext.hex()}")
    
    # Encrypt
    ciphertext = des.encrypt_block(plaintext, key)
    print(f"Ciphertext: {ciphertext.hex()}")
    
    # Decrypt
    decrypted = des.decrypt_block(ciphertext, key)
    print(f"Decrypted: {decrypted.hex()}")
    
    # Verify
    if decrypted == plaintext:
        print("✓ Test passed!")
    else:
        print("✗ Test failed!")


if __name__ == "__main__":
    test_des_core()