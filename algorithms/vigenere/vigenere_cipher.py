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
        
        # Common English words for validation
        self.common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their'
        }

    def clean_text(self, text):
        return ''.join(c.lower() for c in text if c.isalpha())

    # ================= KASISKI EXAMINATION =================
    def kasiski_examination(self, ciphertext, min_len=3, max_len=6, max_keylen=40):
        """Improved with longer sequences and higher max keylen"""
        text = self.clean_text(ciphertext)
        seq_positions = defaultdict(list)

        # Find repeated sequences
        for l in range(min_len, max_len + 1):
            for i in range(len(text) - l):
                seq = text[i:i+l]
                seq_positions[seq].append(i)

        # Calculate spacings
        spacings = []
        for positions in seq_positions.values():
            if len(positions) >= 2:
                for i in range(len(positions) - 1):
                    spacings.append(positions[i+1] - positions[i])

        # Count factors
        factor_count = Counter()
        for space in spacings:
            for k in range(2, min(space + 1, max_keylen + 1)):
                if space % k == 0:
                    factor_count[k] += 1

        # Return top candidates
        return [k for k, _ in factor_count.most_common(15)]

    # ================= INDEX OF COINCIDENCE =================
    def calculate_ic(self, text):
        n = len(text)
        if n <= 1:
            return 0
        freq = Counter(text)
        return sum(v * (v - 1) for v in freq.values()) / (n * (n - 1))

    def ic_analysis(self, ciphertext, max_keylen=40):
        """Extended max_keylen and better scoring"""
        text = self.clean_text(ciphertext)
        results = []

        for k in range(1, min(max_keylen + 1, len(text) // 2)):
            groups = ['' for _ in range(k)]
            for i, c in enumerate(text):
                groups[i % k] += c
            
            # Calculate average IC
            avg_ic = sum(self.calculate_ic(g) for g in groups if len(g) > 1) / k
            
            # Score based on closeness to English IC
            ic_diff = abs(avg_ic - self.IC_ENGLISH)
            results.append((k, avg_ic, ic_diff))

        # Sort by IC difference (closest to English)
        results.sort(key=lambda x: x[2])
        return [k for k, _, _ in results[:15]]

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
            if expected > 0:
                chi2 += ((observed - expected) ** 2) / expected
        return chi2

    # ================= WORD SCORE =================
    def word_score(self, text):
        """Calculate percentage of common English words"""
        words = text.lower().split()
        if not words:
            return 0
        
        valid_words = sum(1 for w in words if ''.join(c for c in w if c.isalpha()) in self.common_words)
        return (valid_words / len(words)) * 100

    # ================= FIND KEY =================
    def crack_caesar(self, text):
        """Find best shift for Caesar cipher using chi-squared"""
        if not text:
            return 0
            
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
        """Extract key of given length"""
        text = self.clean_text(ciphertext)
        
        if keylen > len(text):
            return 'a' * keylen
        
        groups = ['' for _ in range(keylen)]

        for i, c in enumerate(text):
            groups[i % keylen] += c

        key = ''
        for g in groups:
            if g:  # Check if group is not empty
                shift = self.crack_caesar(g)
                key += chr(shift + ord('a'))
            else:
                key += 'a'

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

    # ================= SCORING =================
    def score_plaintext(self, plaintext):
        """Composite score: lower is better"""
        clean = self.clean_text(plaintext)
        
        chi2 = self.chi_squared(clean)
        word_pct = self.word_score(plaintext)
        
        # Composite: chi-squared (lower is better) - word percentage bonus
        composite = chi2 - (word_pct * 0.1)
        
        return composite, chi2, word_pct

    # ================= MAIN CRACK =================
    def crack(self, ciphertext, max_keylen=40):
        """
        Improved cracking algorithm:
        - Tests more key length candidates
        - Better scoring mechanism
        - Handles longer keys
        """
        print("Starting Vigenere cipher crack...")
        
        # Get key length candidates from both methods
        print("Running Kasiski examination...")
        kasiski_keys = self.kasiski_examination(ciphertext, max_keylen=max_keylen)
        
        print("Running IC analysis...")
        ic_keys = self.ic_analysis(ciphertext, max_keylen=max_keylen)

        # Combine candidates (prioritize those in both)
        candidate_lengths = []
        
        # First add keys that appear in both methods
        for k in kasiski_keys:
            if k in ic_keys and k not in candidate_lengths:
                candidate_lengths.append(k)
        
        # Then add remaining IC candidates
        for k in ic_keys:
            if k not in candidate_lengths:
                candidate_lengths.append(k)
        
        # Add remaining Kasiski candidates
        for k in kasiski_keys:
            if k not in candidate_lengths:
                candidate_lengths.append(k)
        
        # Ensure we have enough candidates
        if not candidate_lengths:
            candidate_lengths = list(range(2, min(21, len(self.clean_text(ciphertext)) // 10)))
        
        print(f"Testing {min(len(candidate_lengths), 10)} key length candidates: {candidate_lengths[:10]}")

        best_key = ''
        best_plain = ''
        best_score = float('inf')
        all_results = []

        # Test more candidates (top 10 instead of 3)
        for klen in candidate_lengths[:10]:
            key = self.find_key(ciphertext, klen)
            plain = self.decrypt(ciphertext, key)
            
            composite, chi2, word_pct = self.score_plaintext(plain)
            
            all_results.append({
                'keylen': klen,
                'key': key,
                'plaintext': plain,
                'composite': composite,
                'chi2': chi2,
                'word_pct': word_pct
            })
            
            if composite < best_score:
                best_score = composite
                best_key = key
                best_plain = plain

        # Show top 3 results
        all_results.sort(key=lambda x: x['composite'])
        print("\n=== Top 3 Candidates ===")
        for i, r in enumerate(all_results[:3], 1):
            print(f"\n#{i} Key length: {r['keylen']}")
            print(f"Key: {r['key']}")
            print(f"Chi-squared: {r['chi2']:.2f} | Word%: {r['word_pct']:.1f}% | Score: {r['composite']:.2f}")
            preview = r['plaintext'][:150].replace('\n', ' ')
            print(f"Preview: {preview}...")

        return best_key, best_plain


# ================= FILE HELPER =================

def crack_from_file(input_file, output_file):
    """Crack Vigenere cipher from file"""
    print(f"Reading ciphertext from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        ciphertext = f.read()
    
    print(f"Ciphertext length: {len(ciphertext)} characters")

    cipher = VigenereCipher()
    key, plaintext = cipher.crack(ciphertext)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(key + '\n')
        f.write(plaintext)
    
    print(f"\n✓ Results saved to: {output_file}")
    print(f"✓ Found key: {key} (length: {len(key)})")

    return key, plaintext


# ================= TESTING =================
if __name__ == "__main__":
    # Test with sample
    cipher = VigenereCipher()
    
    # Test case with longer key
    original = "The quick brown fox jumps over the lazy dog. This is a test of the Vigenere cipher with a longer key."
    key = "SECRETKEY"
    
    # Encrypt
    encrypted = cipher.decrypt(original, key)  # Using decrypt as encrypt (symmetric)
    print(f"Original: {original}")
    print(f"Key: {key}")
    print(f"Encrypted: {encrypted}")
    
    # Crack
    cracked_key, cracked_plain = cipher.crack(encrypted)
    print(f"\n✓ Cracked key: {cracked_key}")
    print(f"✓ Decrypted: {cracked_plain}")