from collections import Counter, defaultdict
import math

class VigenereCipher:
    def __init__(self):
        # English letter frequency
        self.english_freq = {
            'a': 0.0817, 'b': 0.0149, 'c': 0.0278, 'd': 0.0425, 'e': 0.1270,
            'f': 0.0223, 'g': 0.0202, 'h': 0.0609, 'i': 0.0697, 'j': 0.0015,
            'k': 0.0077, 'l': 0.0403, 'm': 0.0241, 'n': 0.0675, 'o': 0.0751,
            'p': 0.0193, 'q': 0.0010, 'r': 0.0599, 's': 0.0633, 't': 0.0906,
            'u': 0.0276, 'v': 0.0098, 'w': 0.0236, 'x': 0.0015, 'y': 0.0197,
            'z': 0.0007
        }
        self.IC_ENGLISH = 0.0686

    def clean_text(self, text):
        return ''.join(c.lower() for c in text if c.isalpha())

    # ================= KASISKI EXAMINATION =================
    def kasiski_examination(self, ciphertext, min_len=3, max_len=5, max_keylen=30):
        text = self.clean_text(ciphertext)
        seq_positions = defaultdict(list)

        for l in range(min_len, max_len + 1):
            for i in range(len(text) - l):
                seq = text[i:i+l]
                seq_positions[seq].append(i)

        spacings = []
        for positions in seq_positions.values():
            if len(positions) >= 2:
                for i in range(len(positions) - 1):
                    spacings.append(positions[i+1] - positions[i])

        factor_count = Counter()
        for space in spacings:
            for k in range(2, min(space, max_keylen + 1)):
                if space % k == 0:
                    factor_count[k] += 1

        return [k for k, _ in factor_count.most_common(10)]

    # ================= INDEX OF COINCIDENCE =================
    def calculate_ic(self, text):
        n = len(text)
        if n <= 1:
            return 0
        freq = Counter(text)
        return sum(v * (v - 1) for v in freq.values()) / (n * (n - 1))

    def ic_analysis(self, ciphertext, max_keylen=20):
        text = self.clean_text(ciphertext)
        results = []

        for k in range(1, max_keylen + 1):
            groups = ['' for _ in range(k)]
            for i, c in enumerate(text):
                groups[i % k] += c
            avg_ic = sum(self.calculate_ic(g) for g in groups) / k
            results.append((k, avg_ic))

        results.sort(key=lambda x: abs(x[1] - self.IC_ENGLISH))
        return [k for k, _ in results[:10]]

    # ================= CHI-SQUARED =================
    def chi_squared(self, text):
        n = len(text)
        if n == 0:
            return float('inf')
        freq = Counter(text)
        chi2 = 0
        for c in 'abcdefghijklmnopqrstuvwxyz':
            observed = freq.get(c, 0) / n
            expected = self.english_freq[c]
            chi2 += ((observed - expected) ** 2) / expected
        return chi2

    # ================= FIND KEY =================
    def crack_caesar(self, text):
        best_shift = 0
        best_score = float('inf')

        for shift in range(26):
            decrypted = ''.join(chr((ord(c) - ord('a') - shift) % 26 + ord('a')) for c in text)
            score = self.chi_squared(decrypted)
            if score < best_score:
                best_score = score
                best_shift = shift

        return best_shift

    def find_key(self, ciphertext, keylen):
        text = self.clean_text(ciphertext)
        groups = ['' for _ in range(keylen)]

        for i, c in enumerate(text):
            groups[i % keylen] += c

        key = ''
        for g in groups:
            shift = self.crack_caesar(g)
            key += chr(shift + ord('a'))

        return key

    # ================= DECRYPT =================
    def decrypt(self, ciphertext, key):
        result = []
        ki = 0
        key = key.lower()

        for c in ciphertext:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                shift = ord(key[ki % len(key)]) - ord('a')
                result.append(chr((ord(c) - base - shift) % 26 + base))
                ki += 1
            else:
                result.append(c)
        return ''.join(result)

    # ================= MAIN CRACK =================
    def crack(self, ciphertext):
        kasiski_keys = self.kasiski_examination(ciphertext)
        ic_keys = self.ic_analysis(ciphertext)

        candidate_lengths = [k for k in kasiski_keys if k in ic_keys]
        if not candidate_lengths:
            candidate_lengths = ic_keys[:3]

        best_key = ''
        best_plain = ''
        best_score = float('inf')

        for klen in candidate_lengths[:3]:
            key = self.find_key(ciphertext, klen)
            plain = self.decrypt(ciphertext, key)
            score = self.chi_squared(self.clean_text(plain))

            if score < best_score:
                best_score = score
                best_key = key
                best_plain = plain

        return best_key, best_plain


# ================= FILE HELPER =================

def crack_from_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        ciphertext = f.read()

    cipher = VigenereCipher()
    key, plaintext = cipher.crack(ciphertext)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(key + '\n')
        f.write(plaintext)

    return key, plaintext
