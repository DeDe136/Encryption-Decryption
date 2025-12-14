"""
Caesar Cipher - Brute Force Attack (Improved Version)
Cải tiến: Thêm bigram analysis và cải thiện scoring mechanism
"""

class CaesarCipher:
    def __init__(self):
        # Tần suất chữ cái tiếng Anh (%)
        self.english_freq = {
            'e': 12.70, 't': 9.06, 'a': 8.17, 'o': 7.51, 'i': 6.97,
            'n': 6.75, 's': 6.33, 'h': 6.09, 'r': 5.99, 'd': 4.25,
            'l': 4.03, 'c': 2.78, 'u': 2.76, 'm': 2.41, 'w': 2.36,
            'f': 2.23, 'g': 2.02, 'y': 1.97, 'p': 1.93, 'b': 1.29,
            'v': 0.98, 'k': 0.77, 'j': 0.15, 'x': 0.15, 'q': 0.10, 'z': 0.07
        }
        
        # Bigrams phổ biến trong tiếng Anh
        self.common_bigrams = {
            'th', 'he', 'in', 'er', 'an', 're', 'on', 'at', 'en', 'nd',
            'ti', 'es', 'or', 'te', 'of', 'ed', 'is', 'it', 'al', 'ar',
            'st', 'to', 'nt', 'ng', 'se', 'ha', 'as', 'ou', 'io', 'le'
        }
        
        # Từ phổ biến để kiểm tra
        self.common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
            'was', 'are', 'been', 'has', 'had', 'were', 'said', 'can', 'what', 'so'
        }
    
    def decrypt_with_key(self, ciphertext, key):
        """Giải mã với một khóa cụ thể"""
        plaintext = []
        
        for char in ciphertext:
            if char.isupper():
                shifted = (ord(char) - ord('A') - key) % 26
                plaintext.append(chr(shifted + ord('A')))
            elif char.islower():
                shifted = (ord(char) - ord('a') - key) % 26
                plaintext.append(chr(shifted + ord('a')))
            else:
                plaintext.append(char)
        
        return ''.join(plaintext)
    
    def calculate_frequency_score(self, text):
        """Tính điểm dựa trên tần suất chữ cái (chi-squared test)"""
        text_lower = text.lower()
        letter_count = {}
        total_letters = 0
        
        for char in text_lower:
            if char.isalpha():
                letter_count[char] = letter_count.get(char, 0) + 1
                total_letters += 1
        
        if total_letters == 0:
            return float('inf')
        
        # Chi-squared statistic - càng gần 0 càng giống tiếng Anh
        chi_squared = 0
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            observed = letter_count.get(letter, 0) / total_letters * 100
            expected = self.english_freq[letter]
            chi_squared += ((observed - expected) ** 2) / expected
        
        return chi_squared
    
    def calculate_bigram_score(self, text):
        """Tính điểm dựa trên bigrams phổ biến"""
        text_lower = ''.join(c for c in text.lower() if c.isalpha())
        
        if len(text_lower) < 2:
            return 0
        
        bigram_count = 0
        total_bigrams = len(text_lower) - 1
        
        for i in range(len(text_lower) - 1):
            bigram = text_lower[i:i+2]
            if bigram in self.common_bigrams:
                bigram_count += 1
        
        return (bigram_count / total_bigrams * 100) if total_bigrams > 0 else 0
    
    def calculate_word_score(self, text):
        """Tính điểm dựa trên số từ hợp lệ"""
        words = text.lower().split()
        valid_words = sum(1 for word in words if self._clean_word(word) in self.common_words)
        
        if len(words) == 0:
            return 0
        
        return valid_words / len(words) * 100
    
    def _clean_word(self, word):
        """Loại bỏ dấu câu khỏi từ"""
        return ''.join(char for char in word if char.isalpha())
    
    def calculate_composite_score(self, freq_score, bigram_score, word_score):
        """
        Tính điểm tổng hợp với trọng số cải tiến
        Score càng THẤP càng TỐT
        """
        # Normalize frequency score (chi-squared thường trong khoảng 0-1000+)
        normalized_freq = freq_score / 10
        
        # Word score và bigram score càng cao càng tốt, nên đảo ngược
        word_penalty = 100 - word_score
        bigram_penalty = 100 - bigram_score
        
        # Trọng số: word > bigram > frequency
        composite = (word_penalty * 3.0) + (bigram_penalty * 2.0) + (normalized_freq * 1.0)
        
        return composite
    
    def brute_force(self, ciphertext):
        """
        Thử tất cả 26 khóa và trả về kết quả tốt nhất
        Returns: (key, plaintext, results)
        """
        results = []
        
        for key in range(26):
            plaintext = self.decrypt_with_key(ciphertext, key)
            
            # Tính các điểm thành phần
            freq_score = self.calculate_frequency_score(plaintext)
            bigram_score = self.calculate_bigram_score(plaintext)
            word_score = self.calculate_word_score(plaintext)
            
            # Tính điểm tổng hợp
            composite_score = self.calculate_composite_score(freq_score, bigram_score, word_score)
            
            results.append({
                'key': key,
                'plaintext': plaintext,
                'freq_score': freq_score,
                'bigram_score': bigram_score,
                'word_score': word_score,
                'composite_score': composite_score
            })
        
        # Sắp xếp theo composite score (thấp nhất = tốt nhất)
        results.sort(key=lambda x: x['composite_score'])
        
        best_result = results[0]
        return best_result['key'], best_result['plaintext'], results
    
    def crack(self, ciphertext):
        """
        Hàm chính để crack Caesar cipher
        Returns: (key, plaintext)
        """
        key, plaintext, all_results = self.brute_force(ciphertext)
        
        # In ra top 5 kết quả tốt nhất
        print("\n=== Top 5 Candidates ===")
        
        for i, result in enumerate(all_results[:5], 1):
            print(f"\n#{i} - Key: {result['key']}")
            print(f"  Word Score: {result['word_score']:.1f}% | Bigram Score: {result['bigram_score']:.1f}%")
            print(f"  Freq Score: {result['freq_score']:.2f} | Composite: {result['composite_score']:.2f}")
            preview = result['plaintext'][:150].replace('\n', ' ')
            print(f"  Preview: {preview}...")
        
        return key, plaintext


def crack_from_file(input_file, output_file):
    """
    Crack Caesar cipher từ file và ghi kết quả
    
    Output format:
    - Dòng 1: khóa k
    - Dòng 2+: plaintext
    """
    print(f"Reading ciphertext from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        ciphertext = f.read()
    
    print(f"Ciphertext length: {len(ciphertext)} characters")
    
    # Crack
    cipher = CaesarCipher()
    key, plaintext = cipher.crack(ciphertext)
    
    # Ghi kết quả
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{key}\n")
        f.write(plaintext)
    
    print(f"\n✓ Results saved to: {output_file}")
    print(f"✓ Best key found: {key}")
    
    return key, plaintext


# Test với ví dụ
if __name__ == "__main__":
    # Ví dụ test nhanh
    cipher = CaesarCipher()
    
    # Test case
    test_ciphertext = "Wkh txlfn eurzq ira mxpsv ryhu wkh odcb grj"
    print("Test Ciphertext:", test_ciphertext)
    key, plaintext = cipher.crack(test_ciphertext)
    print(f"\n✓ FINAL ANSWER: Key = {key}")
    print(f"✓ Plaintext: {plaintext}")