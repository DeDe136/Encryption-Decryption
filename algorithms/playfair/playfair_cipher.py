# --- CÁC HÀM XỬ LÝ LOGIC ---

def is_ascii_letter(char):
    """Kiểm tra ký tự A-Z không dấu"""
    return 'A' <= char.upper() <= 'Z'

def is_ascii_alnum(char):
    """Kiểm tra ký tự A-Z hoặc 0-9 không dấu"""
    c = char.upper()
    return ('A' <= c <= 'Z') or ('0' <= c <= '9')

def generate_matrix_5x5(key):
    key = ''.join([c.upper() for c in key if is_ascii_letter(c)])
    key = key.replace('J', 'I')
    key_unique = []
    for c in key:
        if c not in key_unique: key_unique.append(c)
    alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ' 
    for c in alphabet:
        if c not in key_unique: key_unique.append(c)
    matrix = [key_unique[i:i+5] for i in range(0, 25, 5)]
    return matrix

def generate_matrix_6x6(key):
    key = ''.join([c.upper() for c in key if is_ascii_alnum(c)])
    key_unique = []
    for c in key:
        if c not in key_unique: key_unique.append(c)
    alphanumeric = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    for c in alphanumeric:
        if c not in key_unique: key_unique.append(c)
    matrix = [key_unique[i:i+6] for i in range(0, 36, 6)]
    return matrix

def display_matrix(matrix):
    print("\nMa trận:")
    for row in matrix: print(' '.join(row))

def find_position(matrix, char):
    for i, row in enumerate(matrix):
        for j, c in enumerate(row):
            if c == char: return i, j
    return None, None

# --- HÀM XỬ LÝ VĂN BẢN (DÙNG CHUNG CHO CẢ MÃ HÓA VÀ GIẢI MÃ) ---

def process_plaintext_5x5(text, sep1='X', sep2='Y'):
    """Xử lý văn bản 5x5: Tách cặp, chèn sep1/sep2 nếu trùng hoặc lẻ"""
    filtered_text = []
    for char in text:
        if is_ascii_letter(char):
            filtered_text.append(char.upper().replace('J', 'I'))
    text = ''.join(filtered_text)
    
    pairs = []
    inserted_indices = [] 
    i = 0
    char_count = 0 
    
    while i < len(text):
        a = text[i]
        if i + 1 < len(text):
            b = text[i + 1]
            if a == b:
                if a == sep1: pairs.append(a + sep2)
                else: pairs.append(a + sep1)
                inserted_indices.append(char_count + 1)
                i += 1
                char_count += 2
            else:
                pairs.append(a + b)
                i += 2
                char_count += 2
        else:
            if a == sep1: pairs.append(a + sep2) 
            else: pairs.append(a + sep1) 
            inserted_indices.append(char_count + 1)
            i += 1
            char_count += 2
    
    return pairs, inserted_indices

def process_plaintext_6x6(text, sep1='X', sep2='Y'):
    """Xử lý văn bản 6x6: Tách cặp, chèn sep1/sep2 nếu trùng hoặc lẻ"""
    text = ''.join([c.upper() for c in text if is_ascii_alnum(c)])
    
    pairs = []
    inserted_indices = [] 
    i = 0
    char_count = 0
    
    while i < len(text):
        a = text[i]
        if i + 1 < len(text):
            b = text[i + 1]
            if a == b:
                if a == sep1: pairs.append(a + sep2)
                else: pairs.append(a + sep1)
                inserted_indices.append(char_count + 1)
                i += 1
                char_count += 2
            else:
                pairs.append(a + b)
                i += 2
                char_count += 2
        else:
            if a == sep1: pairs.append(a + sep2) 
            else: pairs.append(a + sep1) 
            inserted_indices.append(char_count + 1)
            i += 1
            char_count += 2
    
    return pairs, inserted_indices

# --- CÁC HÀM TÍNH TOÁN ---

def encrypt_pair(matrix, a, b):
    row_a, col_a = find_position(matrix, a)
    row_b, col_b = find_position(matrix, b)
    if row_a is None or row_b is None: return a + b
    
    size = len(matrix)
    if row_a == row_b: 
        return matrix[row_a][(col_a + 1) % size] + matrix[row_b][(col_b + 1) % size]
    elif col_a == col_b: 
        return matrix[(row_a + 1) % size][col_a] + matrix[(row_b + 1) % size][col_b]
    else: 
        return matrix[row_a][col_b] + matrix[row_b][col_a]

def decrypt_pair(matrix, a, b):
    row_a, col_a = find_position(matrix, a)
    row_b, col_b = find_position(matrix, b)
    if row_a is None or row_b is None: return a + b
    
    size = len(matrix)
    if row_a == row_b: 
        return matrix[row_a][(col_a - 1) % size] + matrix[row_b][(col_b - 1) % size]
    elif col_a == col_b: 
        return matrix[(row_a - 1) % size][col_a] + matrix[(row_b - 1) % size][col_b]
    else: 
        return matrix[row_a][col_b] + matrix[row_b][col_a]

# (Các hàm split_ciphertext... giờ không cần dùng cho logic chính nữa 
# nhưng vẫn giữ lại để tránh lỗi nếu bạn lỡ gọi ở đâu đó khác)
def split_ciphertext_5x5(text):
    text = ''.join([c.upper().replace('J','I') for c in text if is_ascii_letter(c)])
    pairs = [text[i:i+2] for i in range(0, len(text), 2)]
    return pairs

def split_ciphertext_6x6(text):
    text = ''.join([c.upper() for c in text if is_ascii_alnum(c)])
    pairs = [text[i:i+2] for i in range(0, len(text), 2)]
    return pairs

# --- CLI ---

def encrypt_func():
    print("\n=== MÃ HÓA PLAYFAIR ===")
    while True:
        matrix_type = input("\nChọn loại ma trận (5 hoặc 6): ")
        if matrix_type in ['5', '6']: break
        print("Vui lòng chọn 5 hoặc 6!")
    
    key = input("Nhập key: ")
    if matrix_type == '5': matrix = generate_matrix_5x5(key)
    else: matrix = generate_matrix_6x6(key)
    
    display_matrix(matrix)
    
    plaintext = input("\nNhập plaintext: ")
    if matrix_type == '5': pairs, inserted_indices = process_plaintext_5x5(plaintext)
    else: pairs, inserted_indices = process_plaintext_6x6(plaintext)
    
    print(f"\nCác cặp từ plaintext: {' '.join(pairs)}")
    
    ciphertext_pairs = []
    for pair in pairs:
        if len(pair) == 2:
            ciphertext_pairs.append(encrypt_pair(matrix, pair[0], pair[1]))
    
    ciphertext_stream = ''.join(ciphertext_pairs)
    
    # Reconstruct logic
    result = []
    cipher_idx = 0
    for char in plaintext:
        is_valid_char = is_ascii_letter(char) if matrix_type == '5' else is_ascii_alnum(char)
        if is_valid_char:
            if cipher_idx < len(ciphertext_stream):
                encrypted_char = ciphertext_stream[cipher_idx]
                result.append(encrypted_char.lower() if char.islower() else encrypted_char)
                cipher_idx += 1
                while cipher_idx in inserted_indices and cipher_idx < len(ciphertext_stream):
                    result.append(ciphertext_stream[cipher_idx]) 
                    cipher_idx += 1
        else:
            result.append(char)
            
    while cipher_idx < len(ciphertext_stream):
        result.append(ciphertext_stream[cipher_idx])
        cipher_idx += 1
    
    print(f"Chuỗi ciphertext: {' '.join(ciphertext_pairs)}")
    print(f"Kết quả mã hóa: {''.join(result)}")

def decrypt_func():
    print("\n=== GIẢI MÃ PLAYFAIR (Có xử lý chèn ký tự) ===")
    while True:
        matrix_type = input("\nChọn loại ma trận (5 hoặc 6): ")
        if matrix_type in ['5', '6']: break
        print("Vui lòng chọn 5 hoặc 6!")
    
    key = input("Nhập key: ")
    if matrix_type == '5': matrix = generate_matrix_5x5(key)
    else: matrix = generate_matrix_6x6(key)
    
    display_matrix(matrix)
    ciphertext = input("\nNhập ciphertext: ")

    # SỬA ĐỔI TẠI ĐÂY: Dùng process_plaintext để chèn X/Y nếu cần
    if matrix_type == '5':
        pairs, inserted_indices = process_plaintext_5x5(ciphertext)
    else:
        pairs, inserted_indices = process_plaintext_6x6(ciphertext)
    
    print(f"\nCác cặp từ ciphertext: {' '.join(pairs)}")
    
    plaintext_pairs = []
    for pair in pairs:
        if len(pair) == 2:
            decrypted = decrypt_pair(matrix, pair[0], pair[1])
            plaintext_pairs.append(decrypted)
    
    print(f"Chuỗi plaintext: {' '.join(plaintext_pairs)}")
    
    plaintext_stream = ''.join(plaintext_pairs)
    
    # Reconstruct logic (Giống hệt encrypt_func để map lại chữ hoa/thường)
    result = []
    plain_idx = 0
    for char in ciphertext:
        is_valid_char = is_ascii_letter(char) if matrix_type == '5' else is_ascii_alnum(char)
        if is_valid_char:
            if plain_idx < len(plaintext_stream):
                # Map lại chữ hoa thường dựa trên input
                c = plaintext_stream[plain_idx]
                result.append(c.lower() if char.islower() else c)
                plain_idx += 1
                
                # Bỏ qua các ký tự separator đã được chèn vào
                while plain_idx in inserted_indices and plain_idx < len(plaintext_stream):
                    result.append(plaintext_stream[plain_idx])
                    plain_idx += 1
        else:
            result.append(char)
            
    while plain_idx < len(plaintext_stream):
         result.append(plaintext_stream[plain_idx])
         plain_idx += 1
         
    print(f"Kết quả giải mã: {''.join(result)}")

def main():
    while True:
        print("\n" + "="*40)
        print("CHƯƠNG TRÌNH MÃ HÓA PLAYFAIR")
        print("="*40)
        print("1. Mã hóa")
        print("2. Giải mã")
        print("3. Thoát")
        choice = input("\nChọn chức năng (1-3): ")
        if choice == '1': encrypt_func()
        elif choice == '2': decrypt_func()
        elif choice == '3':
            print("\nCảm ơn bạn đã sử dụng chương trình!")
            break
        else: print("\nLựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()