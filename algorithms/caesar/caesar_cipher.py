"""
Caesar Cipher - Brute Force Attack
Thuật toán: Thử tất cả 26 khóa có thể và chọn kết quả hợp lý nhất
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
        
        # Từ phổ biến để kiểm tra
        self.common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their'
        }
    
    def decrypt_with_key(self, ciphertext, key):
        """Giải mã với một khóa cụ thể"""
        plaintext = []
        
        for char in ciphertext:
            if char.isupper():
                # Chữ hoa A-Z
                shifted = (ord(char) - ord('A') - key) % 26
                plaintext.append(chr(shifted + ord('A')))
            elif char.islower():
                # Chữ thường a-z
                shifted = (ord(char) - ord('a') - key) % 26
                plaintext.append(chr(shifted + ord('a')))
            else:
                # Giữ nguyên ký tự khác (dấu câu, số, khoảng trắng)
                plaintext.append(char)
        
        return ''.join(plaintext)
    
    def calculate_frequency_score(self, text):
        """Tính điểm dựa trên tần suất chữ cái"""
        text_lower = text.lower()
        letter_count = {}
        total_letters = 0
        
        # Đếm tần suất
        for char in text_lower:
            if char.isalpha():
                letter_count[char] = letter_count.get(char, 0) + 1
                total_letters += 1
        
        if total_letters == 0:
            return 0
        
        # Tính chi-squared statistic
        score = 0
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            observed = letter_count.get(letter, 0) / total_letters * 100
            expected = self.english_freq[letter]
            score += ((observed - expected) ** 2) / expected
        
        return score
    
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
    
    def brute_force(self, ciphertext):
        """
        Thử tất cả 26 khóa và trả về kết quả tốt nhất
        Returns: (key, plaintext, score)
        """
        best_key = 0
        best_plaintext = ""
        best_score = float('inf')
        
        results = []
        
        for key in range(26):
            plaintext = self.decrypt_with_key(ciphertext, key)
            
            # Tính điểm tổng hợp
            freq_score = self.calculate_frequency_score(plaintext)
            word_score = self.calculate_word_score(plaintext)
            
            # Điểm càng thấp càng tốt (chi-squared)
            # Điểm từ càng cao càng tốt
            combined_score = freq_score - (word_score * 5)  # Ưu tiên word score
            
            results.append({
                'key': key,
                'plaintext': plaintext,
                'freq_score': freq_score,
                'word_score': word_score,
                'combined_score': combined_score
            })
            
            if combined_score < best_score:
                best_score = combined_score
                best_key = key
                best_plaintext = plaintext
        
        return best_key, best_plaintext, results
    
    def crack(self, ciphertext):
        """
        Hàm chính để crack Caesar cipher
        Returns: (key, plaintext)
        """
        key, plaintext, all_results = self.brute_force(ciphertext)
        
        # In ra top 3 kết quả tốt nhất để kiểm tra
        print("\n=== Top 3 Candidates ===")
        sorted_results = sorted(all_results, key=lambda x: x['combined_score'])
        
        for i, result in enumerate(sorted_results[:3], 1):
            print(f"\n#{i} - Key: {result['key']}")
            print(f"Word Score: {result['word_score']:.2f}%")
            print(f"Frequency Score: {result['freq_score']:.2f}")
            preview = result['plaintext'][:200].replace('\n', ' ')
            print(f"Preview: {preview}...")
        
        return key, plaintext


def crack_from_file(input_file, output_file):
    """
    Crack Caesar cipher từ file và ghi kết quả
    Theo đúng format yêu cầu của Lab06
    
    Output format:
    - Dòng 1: khóa k
    - Dòng 2+: plaintext
    """
    # Đọc ciphertext
    print(f"Reading ciphertext from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        ciphertext = f.read()
    
    print(f"Ciphertext length: {len(ciphertext)} characters")
    
    # Crack
    cipher = CaesarCipher()
    key, plaintext = cipher.crack(ciphertext)
    
    # Ghi kết quả theo format yêu cầu
    with open(output_file, 'w', encoding='utf-8') as f:
        # Dòng 1: khóa
        f.write(f"{key}\n")
        # Dòng 2+: plaintext
        f.write(plaintext)
    
    print(f"\n✓ Results saved to: {output_file}")
    print(f"Found key: {key}")
    
    return key, plaintext