# AES (Advanced Encryption Standard) - Giải thích thuật toán

## 📌 Tổng quan
AES là **block cipher** hiện đại nhất:
- Block size: 128 bits (16 bytes)
- Key sizes: 128, 192, hoặc 256 bits
- Số rounds: 10, 12, hoặc 14 (tùy key size)
- **Chuẩn mã hóa của Mỹ từ 2001 đến nay**

**Implementation của chúng ta:** AES-128 (10 rounds)

---

## 🎯 Bài toán của chúng ta
**Chức năng:** Mã hóa/Giải mã file với AES-128
**Input:** Plaintext/Ciphertext + Key (16 bytes)
**Output:** Ciphertext/Plaintext
**Modes:** ECB hoặc CBC

---

## 🏗️ Kiến trúc AES

### **Cấu trúc tổng quan:**
```
Plaintext (128 bits = 16 bytes)
    ↓
[Chuyển thành State matrix 4×4]
    ↓
[AddRoundKey (Round 0)]
    ↓
[9 Main Rounds]
    ├─ SubBytes
    ├─ ShiftRows
    ├─ MixColumns
    └─ AddRoundKey
    ↓
[Final Round (Round 10)]
    ├─ SubBytes
    ├─ ShiftRows
    └─ AddRoundKey (NO MixColumns!)
    ↓
Ciphertext (128 bits)
```

**Khác DES:**
- Không dùng Feistel Network
- Xử lý cả block mỗi round (không chia L/R)
- Dùng Galois Field arithmetic

---

## 📊 STATE MATRIX

AES hoạt động trên **State** - ma trận 4×4 bytes:

```
Plaintext: [b0, b1, b2, ..., b15]  (16 bytes)
    ↓
State (column-major):
    ┌─────────────────┐
    │ b0  b4  b8  b12 │
    │ b1  b5  b9  b13 │
    │ b2  b6  b10 b14 │
    │ b3  b7  b11 b15 │
    └─────────────────┘
```

**Lưu ý:** Column-major (theo cột, không phải hàng)

---

## 📊 CÁC PHÉP BIẾN ĐỔI

### 1. **SubBytes** (Substitution)

Thay từng byte bằng S-box:
```
State[i][j] = SBOX[State[i][j]]
```

**S-box:**
- Bảng tra 256 phần tử
- Phi tuyến (non-linear)
- Tạo confusion

**Ví dụ:**
```
0x53 → SBOX[0x53] = 0xED
```

### 2. **ShiftRows** (Permutation)

Dịch các hàng theo pattern:
```
Row 0: Không dịch    [a b c d] → [a b c d]
Row 1: Dịch trái 1   [e f g h] → [f g h e]
Row 2: Dịch trái 2   [i j k l] → [k l i j]
Row 3: Dịch trái 3   [m n o p] → [p m n o]
```

**Mục đích:** Trộn bytes giữa các columns

### 3. **MixColumns** (Diffusion)

Nhân ma trận với mỗi column trong **Galois Field GF(2⁸):**

```
┌───┐   ┌─────────┐   ┌───┐
│ s0│   │02 03 01 01│   │ s0│
│ s1│ = │01 02 03 01│ × │ s1│
│ s2│   │01 01 02 03│   │ s2│
│ s3│   │03 01 01 02│   │ s3│
└───┘   └─────────┘   └───┘
```

**Galois Field multiplication:**
- Không phải nhân thông thường!
- Dùng XOR và polynomial modulo

**Ví dụ:** Nhân với 02 (trong GF):
```
a * 02 = (a << 1) XOR (0x1B nếu a >= 0x80)
```

**Mục đích:** Mỗi byte output phụ thuộc vào tất cả bytes input của column → **diffusion**

### 4. **AddRoundKey** (Key mixing)

XOR State với Round Key:
```
State[i][j] ^= RoundKey[i][j]
```

**Đơn giản nhưng quan trọng:** Đưa key vào quá trình mã hóa!

---

## 🔑 KEY EXPANSION

Từ key 128-bit ban đầu → tạo 11 round keys (44 words):

```
Original Key: K0, K1, K2, K3  (4 words = 16 bytes)
    ↓
Expand to 44 words: W[0] ... W[43]
    ↓
Round 0 key: W[0..3]
Round 1 key: W[4..7]
...
Round 10 key: W[40..43]
```

**Quá trình expand:**
```python
for i in range(4, 44):
    temp = W[i-1]
    
    if i % 4 == 0:
        # RotWord: xoay trái 1 byte
        temp = [temp[1], temp[2], temp[3], temp[0]]
        
        # SubWord: áp dụng S-box
        temp = [SBOX[b] for b in temp]
        
        # XOR với Rcon (round constant)
        temp[0] ^= RCON[i // 4]
    
    W[i] = W[i-4] XOR temp
```

**RCON (Round Constants):**
```
[0x01, 0x02, 0x04, 0x08, 0x10, 0x20, ...]
```

---

## 💡 Các hàm chính trong code

### `_bytes_to_state(data)`
**Chức năng:** Chuyển 16 bytes thành State 4×4
**Làm gì:**
```python
state[row][col] = data[row + 4*col]  # Column-major!
```

### `_state_to_bytes(state)`
**Chức năng:** Chuyển State về 16 bytes
**Làm gì:** Ngược lại với trên

### `key_expansion(key)`
**Chức năng:** Tạo 44 words từ key
**Làm gì:**
1. Copy 4 words đầu từ key
2. Expand thành 44 words với RotWord, SubWord, Rcon

### `_sub_bytes(state)`
**Chức năng:** SubBytes transformation
**Làm gì:**
```python
for r in range(4):
    for c in range(4):
        state[r][c] = SBOX[state[r][c]]
```

### `_shift_rows(state)`
**Chức năng:** ShiftRows transformation
**Làm gì:**
```python
state[1] = rotate_left(state[1], 1)
state[2] = rotate_left(state[2], 2)
state[3] = rotate_left(state[3], 3)
```

### `_mix_columns(state)`
**Chức năng:** MixColumns transformation
**Làm gì:**
- Nhân ma trận với mỗi column trong GF(2⁸)
- Dùng pre-computed tables (GMUL_2, GMUL_3)

**Công thức:**
```python
s0' = GMUL_2[s0] ^ GMUL_3[s1] ^ s2 ^ s3
s1' = s0 ^ GMUL_2[s1] ^ GMUL_3[s2] ^ s3
s2' = s0 ^ s1 ^ GMUL_2[s2] ^ GMUL_3[s3]
s3' = GMUL_3[s0] ^ s1 ^ s2 ^ GMUL_2[s3]
```

### `_add_round_key(state, round_key)`
**Chức năng:** AddRoundKey transformation
**Làm gì:**
```python
state[r][c] ^= round_key[c][r]
```

### `encrypt_block(plaintext, key)`
**Chức năng:** Mã hóa 1 block (16 bytes)
**Làm gì:**
1. Chuyển thành State
2. Key Expansion
3. AddRoundKey (round 0)
4. Rounds 1-9:
   - SubBytes → ShiftRows → MixColumns → AddRoundKey
5. Round 10 (final):
   - SubBytes → ShiftRows → AddRoundKey (NO MixColumns!)
6. Chuyển về bytes

### **DECRYPTION**

Dùng **inverse transformations:**
- InvSubBytes (dùng INV_SBOX)
- InvShiftRows (dịch phải thay vì trái)
- InvMixColumns (nhân với ma trận nghịch đảo)
- AddRoundKey (giống encryption - vì XOR!)

**Thứ tự rounds ngược lại:** K[10] → K[9] → ... → K[0]

---

## 🎯 Tư duy Encryption Flow

```
Plaintext: "Hello World!!!!!" (16 bytes)
    ↓
[Chuyển thành State 4×4]
    H e l l
    o   W o
    W o r l
    o r l d
    ↓
[Key Expansion: tạo 11 round keys]
    ↓
[Round 0: AddRoundKey với K[0]]
    ↓
[Rounds 1-9:]
    SubBytes    → tra S-box
    ShiftRows   → dịch hàng
    MixColumns  → trộn columns
    AddRoundKey → XOR với K[i]
    ↓
[Round 10 (Final):]
    SubBytes
    ShiftRows
    AddRoundKey (NO MixColumns!)
    ↓
Ciphertext (16 bytes)
```

---

## 🔐 MODES & PADDING

**Giống DES:**
- ECB: Mỗi block độc lập
- CBC: Chaining với IV
- PKCS#7 padding

**Khác biệt:**
- Block size: 16 bytes (vs 8 bytes của DES)
- Padding: thêm 1-16 bytes (vs 1-8 bytes)

---

## 📈 So sánh DES vs AES

| Đặc điểm | DES | AES-128 |
|----------|-----|---------|
| **Block size** | 64 bits | 128 bits |
| **Key size** | 56 bits | 128 bits |
| **Rounds** | 16 | 10 |
| **Structure** | Feistel | SPN |
| **Speed** | Chậm | Nhanh (có AES-NI) |
| **Security** | Yếu | Mạnh |
| **Status** | Deprecated | Current |

**SPN = Substitution-Permutation Network**

---

## 🔒 Bảo mật của AES

### ✅ Điểm mạnh

1. **Key đủ dài:** 128 bits → 2¹²⁸ khả năng (vũ trụ!)
2. **Block size lớn:** 128 bits → ít birthday attack
3. **Thiết kế tối ưu:**
   - SubBytes: confusion (phi tuyến)
   - ShiftRows + MixColumns: diffusion (trộn)
4. **Nhanh:** Có instruction set hỗ trợ (AES-NI)
5. **Đã test kỹ:** 20+ năm không bị phá

### ⚠️ Lưu ý

- **ECB mode:** Vẫn không an toàn (patterns)
- **Side-channel attacks:** Cache timing, power analysis
- **Implementation:** Phải cẩn thận (constant-time)

---

## 🎓 Galois Field GF(2⁸)

**Tại sao dùng GF?**
- Cho phép "chia" và "nghịch đảo"
- Mọi phần tử khác 0 có inverse
- Rất quan trọng cho MixColumns

**Polynomial representation:**
```
Byte 0x53 = x⁶ + x⁴ + x + 1
```

**Irreducible polynomial (AES):**
```
m(x) = x⁸ + x⁴ + x³ + x + 1 (0x11B)
```

**Multiplication example:**
```
0x57 * 0x83 = ... (polynomial multiply)
             ... (mod 0x11B)
             = 0xC1
```

---

## 📝 Kết luận

**AES là king of block ciphers:**
- ✅ An toàn tuyệt đối (với implementation đúng)
- ✅ Nhanh trên mọi platform
- ✅ Linh hoạt (128/192/256 bits)
- ✅ Được tin dùng toàn cầu

**Dùng trong thực tế?** CÓ - everywhere!
- HTTPS/TLS
- VPN
- Disk encryption
- Password managers
- ...

**Bài học:** Thiết kế đẹp + toán học chắc chắn = bảo mật lâu dài!