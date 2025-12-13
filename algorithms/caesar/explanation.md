# Caesar Cipher - Giải thích thuật toán

## 📌 Tổng quan
Caesar Cipher là thuật toán mã hóa đơn giản nhất - mỗi chữ cái được dịch một số vị trí cố định trong bảng chữ cái.

**Ví dụ:** Với key = 3:
- A → D, B → E, C → F, ..., X → A, Y → B, Z → C

---

## 🎯 Bài toán của chúng ta
**Input:** File ciphertext (>5000 ký tự) đã được mã hóa bằng Caesar
**Output:** Tìm key và plaintext gốc

---

## 🔑 Ý tưởng giải quyết

### 1. **Brute Force** (Thử tất cả khóa)
Vì Caesar chỉ có 26 khóa khả dĩ (0-25), ta thử hết:

```python
for key in range(26):
    decrypt_with_key(ciphertext, key)
    # Kiểm tra xem kết quả có hợp lý không
```

### 2. **Đánh giá kết quả** (Scoring)
Làm sao biết kết quả nào đúng? Ta dùng 2 phương pháp:

#### A. **Frequency Analysis** (Phân tích tần suất)
- Tiếng Anh: chữ 'e' xuất hiện nhiều nhất (~12.7%)
- Tính chi-squared: so sánh tần suất thực tế với chuẩn

#### B. **Dictionary Check** (Kiểm tra từ điển)
- Đếm số từ hợp lệ trong bản giải mã
- Bản đúng sẽ có nhiều từ tiếng Anh

---

## 📊 Các hàm chính trong code

### `decrypt_with_key(ciphertext, key)`
**Chức năng:** Giải mã với một khóa cụ thể
**Làm gì:** 
- Duyệt từng ký tự
- Nếu là chữ cái: dịch ngược lại `(char - key) % 26`
- Giữ nguyên dấu câu, số

### `calculate_frequency_score(text)`
**Chức năng:** Tính điểm dựa trên tần suất chữ cái
**Làm gì:**
- Đếm tần suất từng chữ cái
- Tính chi-squared với tần suất chuẩn tiếng Anh
- Điểm càng thấp = càng giống tiếng Anh

### `calculate_word_score(text)`
**Chức năng:** Tính tỷ lệ từ hợp lệ
**Làm gì:**
- Tách text thành các từ
- Đếm bao nhiêu từ có trong dictionary
- Trả về phần trăm

### `brute_force(ciphertext)`
**Chức năng:** Hàm chính - thử tất cả khóa
**Làm gì:**
1. Thử 26 khóa (0-25)
2. Với mỗi khóa:
   - Giải mã
   - Tính frequency_score
   - Tính word_score
   - Tính combined_score = freq - (word * 5)
3. Chọn khóa có score tốt nhất

---

## 💡 Tư duy giải quyết

```
CIPHERTEXT
    ↓
[Thử key = 0] → Score = 150.2  ❌
[Thử key = 1] → Score = 142.1  ❌
[Thử key = 2] → Score = 135.8  ❌
    ...
[Thử key = 13] → Score = 8.3   ✅ (Thấp nhất!)
    ...
[Thử key = 25] → Score = 139.5 ❌
    ↓
KẾT QUẢ: Key = 13
```

**Tại sao thành công?**
- Với text dài (>5000 chữ), tần suất chữ cái rất đặc trưng
- Chỉ có 1 khóa cho kết quả giống tiếng Anh

---

## 🎓 Điểm mạnh/yếu

### ✅ Điểm mạnh
- Đơn giản, nhanh (chỉ 26 lần thử)
- Chắc chắn tìm được key đúng
- Hoạt động tốt với text dài

### ❌ Điểm yếu
- Không tự động 100% với text ngắn
- Cần dictionary/frequency data

---

## 📝 Kết luận
Caesar Cipher rất yếu vì:
- Không gian khóa nhỏ (chỉ 26)
- Giữ nguyên tần suất → dễ phân tích

→ Chỉ dùng để học, không dùng thực tế!