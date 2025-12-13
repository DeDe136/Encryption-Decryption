# Mono-alphabetic Substitution - Giải thích thuật toán

## 📌 Tổng quan
Mono-alphabetic substitution: mỗi chữ cái được thay bằng một chữ khác theo bảng ánh xạ cố định.

**Ví dụ mapping:**
```
Plain:  abcdefghijklmnopqrstuvwxyz
Cipher: qwertyuiopasdfghjklzxcvbnm

"hello" → "itssg"
```

---

## 🎯 Bài toán của chúng ta
**Input:** File ciphertext (>5000 ký tự) đã mã hóa
**Output:** Tìm mapping (26! khả năng) và plaintext

**Độ khó:** Rất cao! 26! ≈ 4×10²⁶ khả năng
→ KHÔNG thể brute force!

---

## 🔑 Ý tưởng giải quyết

### Bước 1: **Frequency Analysis** (Tạo mapping ban đầu)
```
Đếm tần suất trong ciphertext:
x: 15.2%, q: 10.1%, w: 8.5%, ...

So với tiếng Anh:
e: 12.7%, t: 9.1%, a: 8.2%, ...

→ Mapping ban đầu:
x → e (cả hai đều phổ biến nhất)
q → t
w → a
...
```

### Bước 2: **Simulated Annealing** (Tối ưu hóa)
Không dừng ở mapping ban đầu, tiếp tục cải thiện:

```python
current_mapping = initial_mapping
current_score = calculate_score(decrypt(ciphertext, current_mapping))

for iteration in range(50000):
    # 1. Thử swap 2 chữ cái ngẫu nhiên
    new_mapping = swap_two_random_letters(current_mapping)
    
    # 2. Tính score mới
    new_score = calculate_score(decrypt(ciphertext, new_mapping))
    
    # 3. Chấp nhận nếu tốt hơn HOẶC theo xác suất
    if new_score > current_score or random() < probability(temperature):
        current_mapping = new_mapping
        current_score = new_score
```

---

## 📊 Các hàm chính trong code

### `create_initial_mapping(ciphertext)`
**Chức năng:** Tạo mapping ban đầu từ frequency
**Làm gì:**
1. Đếm tần suất trong ciphertext
2. Sắp xếp theo thứ tự giảm dần
3. Map với tần suất tiếng Anh chuẩn
4. Ví dụ: chữ phổ biến nhất → 'e'

**Output:** Dictionary như `{'x':'e', 'q':'t', ...}`

### `calculate_fitness(text)`
**Chức năng:** Đánh giá độ "tiếng Anh" của text
**Làm gì:**
- Dùng **quadgram scoring** (chuỗi 4 chữ cái)
- Ví dụ: "tion", "ther", "that" rất phổ biến
- Tính tổng log-probability của tất cả quadgrams
- Score cao = càng giống tiếng Anh

### `simulated_annealing(...)`
**Chức năng:** Tối ưu hóa mapping
**Làm gì:**
1. Bắt đầu với temperature cao
2. Mỗi iteration:
   - Swap 2 chữ cái ngẫu nhiên
   - Tính score mới
   - Chấp nhận nếu:
     * Score tốt hơn, HOẶC
     * Xác suất = exp(Δscore / temperature)
3. Giảm temperature dần
4. Cuối cùng hội tụ về mapping tốt nhất

**Tại sao dùng Simulated Annealing?**
- Hill climbing có thể bị mắc kẹt ở local maximum
- Simulated annealing cho phép "nhảy" ra ngoài

### `apply_mapping(ciphertext, mapping)`
**Chức năng:** Áp dụng mapping để giải mã
**Làm gì:**
- Duyệt từng ký tự
- Thay thế theo mapping
- Giữ nguyên chữ hoa/thấp

---

## 💡 Tư duy giải quyết

```
CIPHERTEXT
    ↓
[Frequency Analysis]
Initial mapping: score = -8500
    ↓
[Simulated Annealing - 50,000 iterations]
    ↓
Iteration 1000: swap 'd'↔'t', score = -8200 ✅
Iteration 2000: swap 'k'↔'m', score = -8150 ✅
Iteration 3000: swap 'r'↔'b', score = -8180 ❌ (giữ lại theo xác suất)
    ...
Iteration 45000: score = -3200 ✅
    ↓
BEST MAPPING FOUND
    ↓
PLAINTEXT
```

---

## 🎓 Tại sao phương pháp này hiệu quả?

### 1. **Quadgram Scoring rất mạnh**
- "tion" xuất hiện rất nhiều trong tiếng Anh
- Nếu mapping sai, sẽ tạo ra "xkqp" (vô nghĩa)
- Score sẽ rất thấp

### 2. **Simulated Annealing tránh local maximum**
```
Score
  ↑
  |     *  ← Local max (hill climbing dừng ở đây)
  |    / \
  |   /   \___
  |  /        \    **** ← Global max (SA tìm được!)
  | /             /    \
  |/______________/______\___→ Iterations
```

### 3. **Text dài (>5000 chữ) → thống kê chính xác**
- Với text ngắn: tần suất không đủ tin cậy
- Text dài: đảm bảo tất cả bigram/trigram/quadgram xuất hiện

---

## 📈 Độ phức tạp

- **Không gian khóa:** 26! ≈ 4×10²⁶
- **Thời gian:** O(iterations × text_length)
  - 50,000 iterations × 5,000 chars ≈ vài phút
- **Brute force:** KHÔNG THỂ (mất hàng tỷ năm!)

---

## 🎯 Điểm mạnh/yếu

### ✅ Điểm mạnh
- Giải được bài toán "không thể" brute force
- Chính xác với text dài
- Tự động hoàn toàn

### ❌ Điểm yếu
- Cần text dài (>5000 chữ)
- Mất vài phút để chạy
- Không đảm bảo 100% (có thể cần chạy lại)

---

## 📝 Kết luận
Mono-alphabetic mạnh hơn Caesar nhiều (26! vs 26 khóa), nhưng vẫn có thể crack bằng:
1. Phân tích tần suất
2. Tối ưu hóa thông minh (Simulated Annealing)
3. N-gram scoring

→ Không dùng trong thực tế, chỉ để học! 