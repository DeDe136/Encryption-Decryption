"""
Optimized Monoalphabetic Substitution Cipher Cracker
Production-grade implementation with all critical fixes
- Bigram + Trigram scoring (stable for 1k-10k char texts)
- Normalized scoring (prevents length bias)
- Hill Climbing with lateral moves (escapes local maxima)
- Smart frequency-based initialization
- No word scoring during optimization
"""

import random
from collections import Counter

class MonoalphabeticCipher:
    def __init__(self):
        # English letter frequencies (for initialization)
        self.letter_freq = {
            'e': 12.70, 't': 9.06, 'a': 8.17, 'o': 7.51, 'i': 6.97,
            'n': 6.75, 's': 6.33, 'h': 6.09, 'r': 5.99, 'd': 4.25,
            'l': 4.03, 'c': 2.78, 'u': 2.76, 'm': 2.41, 'w': 2.36,
            'f': 2.23, 'g': 2.02, 'y': 1.97, 'p': 1.93, 'b': 1.29,
            'v': 0.98, 'k': 0.77, 'j': 0.15, 'x': 0.15, 'q': 0.10, 'z': 0.07
        }
        
        # Load n-gram data (NO DUPLICATES)
        self.bigrams = self._load_bigrams()
        self.trigrams = self._load_trigrams()
        
        # Floor scores for unseen n-grams
        self.bigram_floor = -10.0
        self.trigram_floor = -12.0
    
    def _load_bigrams(self):
        """Load bigram frequencies - FIXED: No duplicates"""
        bigrams = {
            'th': -1.94, 'he': -2.06, 'in': -2.36, 'er': -2.48, 'an': -2.52,
            're': -2.56, 'on': -2.62, 'at': -2.77, 'en': -2.81, 'nd': -2.88,
            'ti': -2.89, 'es': -2.89, 'or': -2.95, 'te': -3.02, 'of': -3.05,
            'ed': -3.05, 'is': -3.09, 'it': -3.11, 'al': -3.14, 'ar': -3.17,
            'st': -3.19, 'to': -3.20, 'nt': -3.20, 'ng': -3.29, 've': -3.32,
            'se': -3.32, 'ha': -3.32, 'as': -3.39, 'ou': -3.39, 'io': -3.44,
            'le': -3.46, 'co': -3.52, 'me': -3.54, 'de': -3.56, 'hi': -3.58,
            'ri': -3.60, 'ro': -3.62, 'ic': -3.64, 'ne': -3.66, 'ea': -3.68,
            'ra': -3.70, 'ce': -3.72, 'li': -3.74, 'ch': -3.76, 'om': -3.78,
            'll': -3.80, 'ma': -3.82, 'el': -3.84, 'ur': -3.86, 'ns': -3.88,
            'be': -3.90, 'il': -3.92, 'di': -3.94, 'ho': -3.96, 'pe': -3.98,
            'ec': -4.00, 'pr': -4.02, 'no': -4.04, 'ct': -4.06, 'us': -4.08,
            'ac': -4.10, 'ow': -4.12, 'ly': -4.14, 'id': -4.16, 'ot': -4.18,
            'ca': -4.20, 'ts': -4.22, 'so': -4.24, 'wa': -4.26, 'si': -4.28
        }
        return bigrams
    
    def _load_trigrams(self):
        """Load trigram frequencies - FIXED: No duplicates"""
        trigrams = {
            'the': -2.56, 'and': -3.27, 'ing': -3.54, 'ion': -3.63, 'tio': -3.65,
            'ent': -3.67, 'ati': -3.69, 'for': -3.72, 'her': -3.80, 'ter': -3.83,
            'hat': -3.86, 'tha': -3.86, 'ere': -3.92, 'ate': -3.98, 'his': -4.00,
            'con': -4.04, 'res': -4.06, 'ver': -4.08, 'all': -4.12, 'ons': -4.14,
            'nce': -4.16, 'men': -4.18, 'ith': -4.20, 'ted': -4.22, 'ers': -4.24,
            'pro': -4.26, 'thi': -4.28, 'wit': -4.30, 'are': -4.32, 'ess': -4.34,
            'not': -4.36, 'ive': -4.38, 'was': -4.40, 'ect': -4.42, 'rea': -4.44,
            'com': -4.46, 'eve': -4.48, 'per': -4.50, 'int': -4.52, 'est': -4.54,
            'sta': -4.56, 'cti': -4.58, 'ica': -4.60, 'ist': -4.62, 'ear': -4.64,
            'ain': -4.66, 'one': -4.68, 'our': -4.70, 'iti': -4.72, 'rat': -4.74,
            'der': -4.76, 'man': -4.78, 'tiv': -4.80, 'ort': -4.82, 'ble': -4.84,
            'ave': -4.86, 'cal': -4.88, 'tin': -4.90, 'but': -4.92, 'out': -4.94,
            'ine': -4.96, 'par': -4.98, 'own': -5.00, 'can': -5.02, 'ant': -5.04
        }
        return trigrams
    
    def score(self, text):
        """
        Score text using bigrams + trigrams
        FIXED: Normalized by n-gram count (prevents length bias)
        """
        text = text.lower()
        
        # Bigram scoring
        bigram_score = 0.0
        bigram_count = 0
        for i in range(len(text) - 1):
            bg = text[i:i+2]
            if bg.isalpha():
                bigram_score += self.bigrams.get(bg, self.bigram_floor)
                bigram_count += 1
        
        # Trigram scoring
        trigram_score = 0.0
        trigram_count = 0
        for i in range(len(text) - 2):
            tg = text[i:i+3]
            if tg.isalpha():
                trigram_score += self.trigrams.get(tg, self.trigram_floor)
                trigram_count += 1
        
        # CRITICAL FIX: Normalize by count
        if bigram_count > 0:
            bigram_score /= bigram_count
        if trigram_count > 0:
            trigram_score /= trigram_count
        
        # Weighted combination (Trigram more important)
        score = (0.3 * bigram_score) + (0.7 * trigram_score)
        
        return score
    
    def initial_key(self, ciphertext):
        """
        IMPROVED: Smart frequency-based initialization
        Only map top 12 letters, randomize rest (more robust)
        """
        text = ciphertext.lower()
        
        # Count letter frequencies
        freq = Counter(c for c in text if c.isalpha())
        
        # Sort by frequency
        sorted_cipher = [item[0] for item in freq.most_common(26)]
        sorted_english = sorted(self.letter_freq.items(), key=lambda x: x[1], reverse=True)
        sorted_english = [item[0] for item in sorted_english]
        
        # Create mapping - ONLY top 12 (more stable)
        key = {}
        map_count = min(12, len(sorted_cipher))
        
        for i in range(map_count):
            cipher_char = sorted_cipher[i]
            key[cipher_char] = sorted_english[i]
        
        # Rest are random assignment
        all_letters = set('abcdefghijklmnopqrstuvwxyz')
        used_cipher = set(key.keys())
        used_plain = set(key.values())
        
        unused_cipher = list(all_letters - used_cipher)
        unused_plain = list(all_letters - used_plain)
        
        # Shuffle for randomness
        random.shuffle(unused_plain)
        
        for i, cipher_char in enumerate(unused_cipher):
            if i < len(unused_plain):
                key[cipher_char] = unused_plain[i]
        
        # Ensure all 26 letters mapped
        for c in all_letters:
            if c not in key:
                # Find unused plain letter
                for p in all_letters:
                    if p not in key.values():
                        key[c] = p
                        break
        
        return key
    
    def decrypt(self, ciphertext, key):
        """Apply key to decrypt"""
        result = []
        for char in ciphertext:
            if char.islower():
                result.append(key.get(char, char))
            elif char.isupper():
                result.append(key.get(char.lower(), char.lower()).upper())
            else:
                result.append(char)
        return ''.join(result)
    
    def hill_climb(self, ciphertext, key, max_iter=20000):
        """
        FIXED: Hill climbing with lateral moves
        Allows moves with equal score (escapes local maxima better)
        """
        best_key = key.copy()
        best_text = self.decrypt(ciphertext, best_key)
        best_score = self.score(best_text)
        
        letters = list('abcdefghijklmnopqrstuvwxyz')
        no_improve = 0
        
        for iteration in range(max_iter):
            # Random swap
            a, b = random.sample(letters, 2)
            key[a], key[b] = key[b], key[a]
            
            # Evaluate
            text = self.decrypt(ciphertext, key)
            score = self.score(text)
            
            # FIXED: Accept if >= (not just >)
            # This allows lateral moves
            if score >= best_score:
                best_score = score
                best_key = key.copy()
                no_improve = 0
            else:
                # Rollback
                key[a], key[b] = key[b], key[a]
                no_improve += 1
            
            # Early stopping
            if no_improve > 3000:
                break
        
        return best_key, best_score
    
    def crack(self, ciphertext, restarts=20):
        """
        Multi-restart hill climbing
        Standard approach for substitution ciphers
        """
        print("="*60)
        print("CRACKING MONOALPHABETIC SUBSTITUTION")
        print("="*60)
        print(f"Text length: {len(ciphertext)} characters")
        print(f"Restarts: {restarts}")
        print()
        
        best_global_key = None
        best_global_score = float('-inf')
        
        for r in range(restarts):
            # Initialize with smart frequency analysis
            key = self.initial_key(ciphertext)
            
            # Add random perturbation (5-15 swaps)
            for _ in range(random.randint(5, 15)):
                a, b = random.sample('abcdefghijklmnopqrstuvwxyz', 2)
                key[a], key[b] = key[b], key[a]
            
            # Hill climb
            key, score = self.hill_climb(ciphertext, key)
            
            print(f"Restart {r+1:2d}/{restarts}: score = {score:8.4f}")
            
            # Track best
            if score > best_global_score:
                best_global_score = score
                best_global_key = key.copy()
        
        print()
        print("="*60)
        print(f"BEST SCORE: {best_global_score:.4f}")
        print("="*60)
        
        plaintext = self.decrypt(ciphertext, best_global_key)
        return best_global_key, plaintext, best_global_score
    
    def format_key(self, key):
        """Format key for output"""
        return ', '.join(f"{k}->{v}" for k, v in sorted(key.items()))


def crack_from_file(input_file, output_file):
    """
    Crack cipher from file and save result
    Output format:
    Line 1: score
    Line 2: mapping
    Line 3+: plaintext
    """
    print(f"Reading ciphertext from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        ciphertext = f.read()
    
    print(f"Ciphertext length: {len(ciphertext)} characters\n")
    
    # Crack
    cipher = MonoalphabeticCipher()
    key, plaintext, score = cipher.crack(ciphertext)
    
    # Save output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{score:.4f}\n")
        f.write(cipher.format_key(key) + '\n')
        f.write(plaintext)
    
    print(f"\n✓ Results saved to: {output_file}")
    print(f"Final score: {score:.4f}")
    
    return key, plaintext, score


if __name__ == "__main__":
    # Test with sample
    ciphertext = """Gsv hxrvmxv lu xibkgltizksb rh zmxrvmg, yfg rgh nlwvim 
    zkkorxzgrlmh ziv dswvob fhvw rm wrtrgzo xllnfmrxzgrlmh."""
    
    cipher = MonoalphabeticCipher()
    key, plaintext, score = cipher.crack(ciphertext, restarts=10)
    
    print("\n" + "="*60)
    print("RESULT")
    print("="*60)
    print(f"Score: {score:.4f}")
    print(f"\nPlaintext:\n{plaintext}")