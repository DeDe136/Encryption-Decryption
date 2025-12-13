# DES (Data Encryption Standard) - Giải thích thuật toán

## 📌 Tổng quan
DES là **block cipher** đối xứng:
- Block size: 64 bits (8 bytes)
- Key size: 56 bits (thực tế 64 bits, 8 bits parity)
- Số rounds: 16
- Chuẩn mã hóa của Mỹ từ 1977-2001

---

## 🎯 Bài toán của chúng ta
**Chức năng:** Mã hóa/Giải mã file với DES
**Input:** Plaintext/Ciphertext + Key (8 bytes)
**Output:** Ciphertext/Plaintext
**Modes:** ECB hoặc CBC

---

## 🏗️ Kiến trúc DES

### **Cấu trúc tổng quan:**
```
Plaintext (64 bits)
    ↓
[Initial Permutation - IP]
    ↓
[16 Rounds của Feistel Network]
    ↓
[Final Permutation - IP⁻¹]
    ↓
Ciphertext (64 bits)
```

---

## 📊 CÁC THÀNH PHẦN CHÍNH

### 1. **Initial Permutation (IP)**
Hoán vị các bit theo bảng cố định:
```
Bit 1 → vị trí 58
Bit 2 → vị trí 50
...
```
**Mục đích:** Trộn bits ban đầu (không tăng bảo mật, chỉ là truyền thống)

### 2. **Feistel Network (16 Rounds)**

Mỗi round làm 4 việc:

```
Round i:
    L[i-1]  R[i-1]  (32 bits mỗi nửa)
      ↓       ↓
      |   [F-function với K[i]]
      |       ↓
      |   [XOR với L[i-1]]
      |       ↓
      └─────→ XOR
              ↓
            L[i]    R[i]
```

**Đặc điểm Feistel:** 
- Encryption và Decryption dùng cùng cấu trúc
- Chỉ cần đảo ngược thứ tự subkeys

### 3. **F-function (Hàm F)**

Đây là trái tim của DES:

```
Input: R (32 bits) + Subkey K[i] (48 bits)
    ↓
[Expansion E: 32→48 bits]
    ↓
[XOR với K[i]]
    ↓
[S-boxes: 48→32 bits]  ← Phi tuyến!
    ↓
[Permutation P]
    ↓
Output: 32 bits
```

#### **S-boxes (Substitution boxes)**
- 8 S-boxes, mỗi cái: 6 bits → 4 bits
- **Phi tuyến** - thành phần duy nhất không tuyến tính trong DES
- Thiết kế cẩn thận để chống cryptanalysis

**Ví dụ S-box:**
```
Input: 6 bits = 011011
→ Row = bit đầu & cuối = 01 = 1
→ Col = 4 bits giữa = 1101 = 13
→ S1[row=1][col=13] = 5 = 0101
```

### 4. **Key Schedule (Sinh subkeys)**

```
Key (64 bits) → bỏ parity → 56 bits
    ↓
[PC-1: Permuted Choice 1]
    ↓
C[0] (28 bits)  D[0] (28 bits)
    ↓               ↓
For i = 1 to 16:
    Left shift C[i-1], D[i-1]
    ↓
    [PC-2: Permuted Choice 2]
    ↓
    K[i] (48 bits)
```

**Left shifts:**
- Rounds 1,2,9,16: shift 1 bit
- Các rounds khác: shift 2 bits

---

## 📊 MODES OF OPERATION

### **ECB (Electronic Codebook)**
```
Block 1 → [DES] → Cipher 1
Block 2 → [DES] → Cipher 2
Block 3 → [DES] → Cipher 3
```

**Đặc điểm:**
- ✅ Đơn giản, có thể song song
- ❌ Cùng plaintext → cùng ciphertext
- ❌ Không che giấu patterns

### **CBC (Cipher Block Chaining)**
```
        IV
         ↓
Block 1 ⊕ → [DES] → Cipher 1
             ↓
Block 2 ⊕ → [DES] → Cipher 2
             ↓
Block 3 ⊕ → [DES] → Cipher 3
```

**Đặc điểm:**
- ✅ Cùng plaintext → khác ciphertext (nhờ IV)
- ✅ Errors giới hạn trong 2 blocks
- ❌ Không song song được (encryption)

---

## 💡 Các hàm chính trong code

### `_permute(block, table)`
**Chức năng:** Hoán vị bits theo bảng
**Làm gì:**
```python
output[i] = input[table[i] - 1]
```

### `_bytes_to_bits(data)` / `_bits_to_bytes(bits)`
**Chức năng:** Chuyển đổi bytes ↔ bits
**Làm gì:** 
- Bytes to bits: mỗi byte → 8 bits
- Bits to bytes: mỗi 8 bits → 1 byte

### `_generate_subkeys(key_bits)`
**Chức năng:** Tạo 16 subkeys từ key
**Làm gì:**
1. PC-1: 64 bits → 56 bits
2. Chia thành C[0], D[0] (28 bits mỗi nửa)
3. For i = 1..16:
   - Left shift C, D
   - PC-2: 56 bits → 48 bits subkey

### `_s_box_substitution(bits_48)`
**Chức năng:** Áp dụng 8 S-boxes
**Làm gì:**
- Chia 48 bits thành 8 nhóm (6 bits/nhóm)
- Mỗi nhóm → 1 S-box → 4 bits
- Ghép lại → 32 bits

### `_f_function(right_half, subkey)`
**Chức năng:** Hàm F trong Feistel
**Làm gì:**
1. Expansion: 32→48 bits
2. XOR với subkey
3. S-boxes: 48→32 bits
4. Permutation P
5. Return 32 bits

### `_des_round(left, right, subkey)`
**Chức năng:** 1 round của DES
**Làm gì:**
```
new_right = left ⊕ F(right, subkey)
new_left = right
```

### `encrypt_block(plaintext, key)`
**Chức năng:** Mã hóa 1 block (64 bits)
**Làm gì:**
1. Initial Permutation
2. 16 rounds của Feistel
3. Swap left/right
4. Final Permutation

### `decrypt_block(ciphertext, key)`
**Chức năng:** Giải mã 1 block
**Làm gì:**
- Giống encrypt nhưng dùng subkeys ngược (K[16]..K[1])

---

## 🔐 PADDING (PKCS#7)

**Vấn đề:** Plaintext không chia hết cho 8 bytes

**Giải pháp PKCS#7:**
```
Original: [A B C D E]     (5 bytes)
Padded:   [A B C D E 03 03 03]  (8 bytes)
          ↑           ↑ thêm 3 bytes, giá trị = 03
```

**Đặc biệt:** Nếu đúng 8 bytes → thêm 1 block padding!
```
Original: [A B C D E F G H]  (8 bytes)
Padded:   [A B C D E F G H][08 08 08 08 08 08 08 08]
```

---

## 🎯 Tư duy Encryption/Decryption

### **ENCRYPTION (ECB):**
```
Plaintext: "Hello World!" (12 bytes)
    ↓
[PKCS#7 Padding]
"Hello World!\x04\x04\x04\x04" (16 bytes)
    ↓
[Chia thành 2 blocks]
Block 1: "Hello Wo"
Block 2: "rld!\x04\x04\x04\x04"
    ↓
[Encrypt từng block]
Block 1 → DES → Cipher 1
Block 2 → DES → Cipher 2
    ↓
[Chuyển sang hex]
Ciphertext: "a3b5c7d9e1f2..."
```

### **DECRYPTION (CBC):**
```
Ciphertext + IV
    ↓
[Chia thành blocks]
    ↓
For each block:
    Decrypt với DES
    XOR với previous (hoặc IV)
    ↓
[Remove padding]
    ↓
Plaintext
```

---

## 📈 Bảo mật của DES

### ✅ Điểm mạnh (năm 1977)
- S-boxes thiết kế tốt
- 16 rounds đủ chống differential cryptanalysis
- Confusion và diffusion tốt

### ❌ Điểm yếu (ngày nay)
- **Key quá ngắn:** 56 bits → brute force trong vài giờ
- **Block size nhỏ:** 64 bits → sinh birthday attacks với text dài
- **Chậm:** So với AES

### 🔧 Cải tiến
- **3DES:** Áp dụng DES 3 lần → 112/168 bits security
- **AES:** Thay thế DES từ 2001

---

## 📝 Kết luận

DES là thuật toán lịch sử:
- **Thiết kế đẹp:** Feistel network, S-boxes
- **Đã lỗi thời:** Key quá ngắn
- **Di sản:** Nền tảng cho các block ciphers hiện đại

**Dùng trong thực tế?** KHÔNG - dùng AES!
**Học trong lab?** CÓ - hiểu nguyên lý block cipher!