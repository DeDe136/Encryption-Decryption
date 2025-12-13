# Vigenère Cipher - Giải thích thuật toán

## 📌 Tổng quan
Vigenère là **polyalphabetic cipher** - dùng nhiều Caesar ciphers xen kẽ nhau theo một key.

**Ví dụ:**
```
Plaintext:  ATTACKATDAWN
Key:        LEMONLEMONLE (lặp lại)
            ↓ mã hóa từng cặp
Ciphertext: LXFOPVEFRNHR

A + L = L, T + E = X, T + M = F, ...
```

---

## 🎯 Bài toán của chúng ta
**Input:** File ciphertext (>5000 ký tự)
**Output:** Tìm key và plaintext

**Độ khó:** Cao! 
- Không biết độ dài key (có thể 3, 5, 10, ...)
- Với key dài 8: có 26⁸ ≈ 2×10¹¹ khả năng

---

## 🔑 Ý tưởng giải quyết

### **3 bước chính:**

```
[Bước 1] Tìm độ dài key
    ↓
[Bước 2] Chia ciphertext thành các subset
    ↓
[Bước 3] Crack từng subset như Caesar
```

---

## 📊 BƯỚC 1: Tìm độ dài key

### Phương pháp A: **Kasiski Examination**

**Ý tưởng:** Tìm chuỗi lặp lại trong ciphertext

```
Ciphertext: ...ABC...ABC...ABC...
             ↑   ↑   ↑
Position:   100  148  196

Khoảng cách: 48, 48
Ước số của 48: 1,2,3,4,6,8,12,16,24,48
→ Key length có thể là: 6,8,12
```

**Tại sao?** 
Nếu key = "SECRET" (6 chữ), cùng một đoạn plaintext sẽ được mã hóa giống nhau khi cách nhau 6, 12, 18, ... vị trí.

### Phương pháp B: **Index of Coincidence (IC)**

**Ý tưởng:** Đo độ "tiếng Anh" của text

```python
IC = Σ(count[i] * (count[i]-1)) / (n * (n-1))

Tiếng Anh: IC ≈ 0.0686
Random text: IC ≈ 0.0385
```

**Cách dùng:**
```python
for key_length in range(1, 20):
    # Chia ciphertext thành key_length subsets
    subsets = split_by_keylength(ciphertext, key_length)
    
    # Tính IC trung bình
    avg_ic = average([IC(subset) for subset in subsets])
    
    # Key length đúng → IC ≈ 0.0686
```

**Tại sao hiệu quả?**
- Key đúng → mỗi subset là Caesar cipher → giữ tần suất tiếng Anh
- Key sai → subset là text ngẫu nhiên → IC thấp

---

## 📊 BƯỚC 2: Chia thành subsets

Giả sử tìm được key length = 5:

```
Ciphertext: L X F O P V E F R N H R ...
            ↓ ↓ ↓ ↓ ↓
Subset 0:   L   F   V   R       (vị trí 0,5,10,15,...)
Subset 1:     X   O   E   N     (vị trí 1,6,11,16,...)
Subset 2:       F   P   F   H   (vị trí 2,7,12,17,...)
Subset 3:         O   E   R     (vị trí 3,8,13,18,...)
Subset 4:           P   F   R   (vị trí 4,9,14,19,...)
```

**Mỗi subset được mã hóa bởi 1 ký tự trong key → là 1 Caesar cipher!**

---

## 📊 BƯỚC 3: Crack từng subset

Mỗi subset là Caesar cipher → dùng frequency analysis:

```python
def crack_subset(subset):
    best_key = 0
    best_score = infinity
    
    for key in range(26):
        decrypted = caesar_decrypt(subset, key)
        score = chi_squared(decrypted)
        
        if score < best_score:
            best_key = key
            best_score = score
    
    return best_key
```

**Ghép lại:**
```
Subset 0 → key = 11 (L)
Subset 1 → key = 4  (E)
Subset 2 → key = 12 (M)
Subset 3 → key = 14 (O)
Subset 4 → key = 13 (N)

→ KEY = "LEMON" ✅
```

---

## 💡 Các hàm chính trong code

### `find_repeated_sequences(ciphertext)`
**Chức năng:** Tìm chuỗi lặp (Kasiski)
**Làm gì:**
- Duyệt tất cả chuỗi 3-5 ký tự
- Tìm vị trí xuất hiện lặp
- Trả về dictionary: `{"ABC": [100, 148, 196], ...}`

### `calculate_spacings(sequences)`
**Chức năng:** Tính khoảng cách
**Làm gì:**
- Với mỗi chuỗi lặp, tính khoảng cách giữa các lần xuất hiện
- Tìm ước số chung → gợi ý key length

### `calculate_IC(text)`
**Chức năng:** Tính Index of Coincidence
**Làm gì:**
```python
IC = Σ(f[i] * (f[i]-1)) / (n * (n-1))
```
Đo độ "không ngẫu nhiên" của text

### `ic_test_keylength(ciphertext, key_length)`
**Chức năng:** Test một độ dài key cụ thể
**Làm gì:**
1. Chia ciphertext thành `key_length` subsets
2. Tính IC của từng subset
3. Lấy trung bình
4. Nếu gần 0.0686 → key length có thể đúng

### `crack_caesar_subset(subset)`
**Chức năng:** Crack một subset như Caesar
**Làm gì:**
- Thử 26 shifts (0-25)
- Tính chi-squared score cho mỗi shift
- Chọn shift có score tốt nhất

### `crack(ciphertext)`
**Chức năng:** Hàm chính
**Làm gì:**
1. Kasiski → tìm key lengths khả dĩ
2. IC test → xác nhận key lengths
3. Kết hợp → chọn top 3 key lengths
4. Với mỗi key length:
   - Chia subsets
   - Crack từng subset
   - Tạo key
5. Chọn key cho plaintext tốt nhất

---

## 🎯 Tư duy giải quyết

```
CIPHERTEXT (5000+ chars)
    ↓
[Kasiski Examination]
Found repeated "THE" at: 100, 148, 196, ...
Spacings: 48, 48, ...
Factors: 2,3,4,6,8,12,24,48
    ↓
[IC Analysis]
Key length 6: IC = 0.0672 ✅
Key length 8: IC = 0.0510 ❌
Key length 12: IC = 0.0630 ~
    ↓
[Try key_length = 6]
    ↓
Subset 0: "LFVR..." → key = L (11)
Subset 1: "XOEN..." → key = E (4)
Subset 2: "FPFH..." → key = M (12)
Subset 3: "OERQ..." → key = O (14)
Subset 4: "PFRW..." → key = N (13)
Subset 5: "VTAB..." → key = X (23) ❌ score cao
    ↓
Chi-squared = 125.3 ❌
    ↓
[Try key_length = 5]
    ↓
Chi-squared = 18.2 ✅ BEST!
    ↓
KEY = "LEMON"
```

---

## 📈 Độ phức tạp

**Thời gian:**
- Kasiski: O(n²) với text dài n
- IC test: O(20 × n) test tối đa 20 key lengths
- Crack subsets: O(26 × n/k) với k là key length

**Tổng:** O(n²) → vài giây với n=5000

---

## 🎓 Điểm mạnh/yếu

### ✅ Điểm mạnh
- Tự động tìm key length
- Chính xác với text dài
- Không cần biết gì trước

### ❌ Điểm yếu
- Cần text dài (>5000 chars)
- Key ngắn dễ crack hơn key dài
- Không hoạt động nếu key ngẫu nhiên và dài

---

## 📝 Kết luận

Vigenère từng được gọi là "le chiffre indéchiffrable" (mật mã không thể giải), nhưng:

1. **Kasiski (1863)** phát hiện chuỗi lặp
2. **Friedman (1920s)** phát minh IC test
3. **Ngày nay:** crack trong vài giây!

**Bài học:** Tần suất và thống kê là vũ khí mạnh nhất chống mật mã cổ điển!