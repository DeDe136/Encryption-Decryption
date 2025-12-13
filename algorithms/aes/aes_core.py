"""
AES Core Algorithm
Implementation of AES-128 encryption/decryption
Following FIPS 197 standard
"""

from .aes_tables import (
    SBOX, INV_SBOX, RCON,
    GMUL_2, GMUL_3, GMUL_9, GMUL_11, GMUL_13, GMUL_14
)


class AESCore:
    """
    AES-128 Core Implementation
    Block size: 128 bits (16 bytes)
    Key size: 128 bits (16 bytes)
    """
    
    def __init__(self):
        self.Nb = 4  # Number of columns (32-bit words) in State - always 4 for AES
        self.Nk = 4  # Number of 32-bit words in Key - 4 for AES-128
        self.Nr = 10 # Number of rounds - 10 for AES-128
    
    # ==================== KEY EXPANSION ====================
    
    def _rot_word(self, word):
        """Rotate word left by 1 byte: [a0,a1,a2,a3] -> [a1,a2,a3,a0]"""
        return word[1:] + word[:1]
    
    def _sub_word(self, word):
        """Apply S-box to each byte in word"""
        return [SBOX[b] for b in word]
    
    def _xor_words(self, w1, w2):
        """XOR two words"""
        return [b1 ^ b2 for b1, b2 in zip(w1, w2)]
    
    def key_expansion(self, key):
        """
        Expand 128-bit key into 44 words (11 round keys)
        key: 16 bytes
        Returns: list of 44 words (each word = 4 bytes)
        """
        if len(key) != 16:
            raise ValueError(f"Key must be 16 bytes for AES-128, got {len(key)}")
        
        # Initialize with original key (4 words)
        w = []
        for i in range(4):
            w.append(list(key[4*i:4*i+4]))
        
        # Expand to 44 words
        for i in range(4, 44):
            temp = w[i-1][:]
            
            if i % 4 == 0:
                # RotWord + SubWord + Rcon
                temp = self._rot_word(temp)
                temp = self._sub_word(temp)
                temp[0] ^= RCON[i // 4]
            
            w.append(self._xor_words(w[i-4], temp))
        
        return w
    
    def _get_round_key(self, expanded_key, round_num):
        """
        Get round key for specific round
        Returns: 4x4 state matrix
        """
        start_word = round_num * 4
        round_key = []
        
        for col in range(4):
            word = expanded_key[start_word + col]
            round_key.append(word[:])
        
        return round_key
    
    # ==================== STATE OPERATIONS ====================
    
    def _bytes_to_state(self, data):
        """
        Convert 16 bytes to 4x4 state matrix (column-major order)
        [b0, b1, ..., b15] -> [[b0,b4,b8,b12],
                                [b1,b5,b9,b13],
                                [b2,b6,b10,b14],
                                [b3,b7,b11,b15]]
        """
        state = []
        for r in range(4):
            row = []
            for c in range(4):
                row.append(data[r + 4*c])
            state.append(row)
        return state
    
    def _state_to_bytes(self, state):
        """Convert 4x4 state matrix back to 16 bytes"""
        result = []
        for c in range(4):
            for r in range(4):
                result.append(state[r][c])
        return bytes(result)
    
    # ==================== ENCRYPTION OPERATIONS ====================
    
    def _sub_bytes(self, state):
        """Apply S-box to each byte in state"""
        for r in range(4):
            for c in range(4):
                state[r][c] = SBOX[state[r][c]]
        return state
    
    def _shift_rows(self, state):
        """
        Shift rows cyclically to the left
        Row 0: no shift
        Row 1: shift 1
        Row 2: shift 2
        Row 3: shift 3
        """
        state[1] = state[1][1:] + state[1][:1]  # Shift left by 1
        state[2] = state[2][2:] + state[2][:2]  # Shift left by 2
        state[3] = state[3][3:] + state[3][:3]  # Shift left by 3
        return state
    
    def _mix_columns(self, state):
        """
        Mix columns using Galois Field multiplication
        Each column is treated as a polynomial and multiplied by a(x) = {03}x^3 + {01}x^2 + {01}x + {02}
        """
        for c in range(4):
            s0, s1, s2, s3 = state[0][c], state[1][c], state[2][c], state[3][c]
            
            state[0][c] = GMUL_2[s0] ^ GMUL_3[s1] ^ s2 ^ s3
            state[1][c] = s0 ^ GMUL_2[s1] ^ GMUL_3[s2] ^ s3
            state[2][c] = s0 ^ s1 ^ GMUL_2[s2] ^ GMUL_3[s3]
            state[3][c] = GMUL_3[s0] ^ s1 ^ s2 ^ GMUL_2[s3]
        
        return state
    
    def _add_round_key(self, state, round_key):
        """XOR state with round key"""
        for r in range(4):
            for c in range(4):
                state[r][c] ^= round_key[c][r]
        return state
    
    # ==================== DECRYPTION OPERATIONS ====================
    
    def _inv_sub_bytes(self, state):
        """Apply inverse S-box to each byte"""
        for r in range(4):
            for c in range(4):
                state[r][c] = INV_SBOX[state[r][c]]
        return state
    
    def _inv_shift_rows(self, state):
        """Inverse shift rows - shift right instead of left"""
        state[1] = state[1][-1:] + state[1][:-1]  # Shift right by 1
        state[2] = state[2][-2:] + state[2][:-2]  # Shift right by 2
        state[3] = state[3][-3:] + state[3][:-3]  # Shift right by 3
        return state
    
    def _inv_mix_columns(self, state):
        """
        Inverse mix columns
        Multiply by a^-1(x) = {0b}x^3 + {0d}x^2 + {09}x + {0e}
        """
        for c in range(4):
            s0, s1, s2, s3 = state[0][c], state[1][c], state[2][c], state[3][c]
            
            state[0][c] = GMUL_14[s0] ^ GMUL_11[s1] ^ GMUL_13[s2] ^ GMUL_9[s3]
            state[1][c] = GMUL_9[s0] ^ GMUL_14[s1] ^ GMUL_11[s2] ^ GMUL_13[s3]
            state[2][c] = GMUL_13[s0] ^ GMUL_9[s1] ^ GMUL_14[s2] ^ GMUL_11[s3]
            state[3][c] = GMUL_11[s0] ^ GMUL_13[s1] ^ GMUL_9[s2] ^ GMUL_14[s3]
        
        return state
    
    # ==================== MAIN ENCRYPTION/DECRYPTION ====================
    
    def encrypt_block(self, plaintext_block, key):
        """
        Encrypt one 16-byte block
        plaintext_block: 16 bytes
        key: 16 bytes
        Returns: 16 bytes
        """
        if len(plaintext_block) != 16:
            raise ValueError("Block must be 16 bytes")
        
        # Key expansion
        expanded_key = self.key_expansion(key)
        
        # Initialize state
        state = self._bytes_to_state(plaintext_block)
        
        # Initial round key addition
        round_key = self._get_round_key(expanded_key, 0)
        state = self._add_round_key(state, round_key)
        
        # Main rounds (1-9)
        for round_num in range(1, self.Nr):
            state = self._sub_bytes(state)
            state = self._shift_rows(state)
            state = self._mix_columns(state)
            round_key = self._get_round_key(expanded_key, round_num)
            state = self._add_round_key(state, round_key)
        
        # Final round (no MixColumns)
        state = self._sub_bytes(state)
        state = self._shift_rows(state)
        round_key = self._get_round_key(expanded_key, self.Nr)
        state = self._add_round_key(state, round_key)
        
        return self._state_to_bytes(state)
    
    def decrypt_block(self, ciphertext_block, key):
        """
        Decrypt one 16-byte block
        ciphertext_block: 16 bytes
        key: 16 bytes
        Returns: 16 bytes
        """
        if len(ciphertext_block) != 16:
            raise ValueError("Block must be 16 bytes")
        
        # Key expansion
        expanded_key = self.key_expansion(key)
        
        # Initialize state
        state = self._bytes_to_state(ciphertext_block)
        
        # Initial round key addition (with last round key)
        round_key = self._get_round_key(expanded_key, self.Nr)
        state = self._add_round_key(state, round_key)
        
        # Main rounds in reverse (9-1)
        for round_num in range(self.Nr - 1, 0, -1):
            state = self._inv_shift_rows(state)
            state = self._inv_sub_bytes(state)
            round_key = self._get_round_key(expanded_key, round_num)
            state = self._add_round_key(state, round_key)
            state = self._inv_mix_columns(state)
        
        # Final round (no InvMixColumns)
        state = self._inv_shift_rows(state)
        state = self._inv_sub_bytes(state)
        round_key = self._get_round_key(expanded_key, 0)
        state = self._add_round_key(state, round_key)
        
        return self._state_to_bytes(state)


def test_aes_core():
    """Test AES core with standard test vectors"""
    aes = AESCore()
    
    # FIPS 197 test vector
    key = bytes.fromhex('000102030405060708090a0b0c0d0e0f')
    plaintext = bytes.fromhex('00112233445566778899aabbccddeeff')
    expected_ciphertext = bytes.fromhex('69c4e0d86a7b0430d8cdb78070b4c55a')
    
    print("Testing AES-128 Core...")
    print(f"Key:       {key.hex()}")
    print(f"Plaintext: {plaintext.hex()}")
    
    # Encrypt
    ciphertext = aes.encrypt_block(plaintext, key)
    print(f"Ciphertext: {ciphertext.hex()}")
    print(f"Expected:   {expected_ciphertext.hex()}")
    
    if ciphertext == expected_ciphertext:
        print("✓ Encryption test passed!")
    else:
        print("✗ Encryption test failed!")
        return
    
    # Decrypt
    decrypted = aes.decrypt_block(ciphertext, key)
    print(f"Decrypted:  {decrypted.hex()}")
    
    if decrypted == plaintext:
        print("✓ Decryption test passed!")
    else:
        print("✗ Decryption test failed!")
        return
    
    print("\n✓ All AES core tests passed!")


if __name__ == "__main__":
    test_aes_core()