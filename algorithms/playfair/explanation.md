# 🔐 GIẢI THÍCH CHI TIẾT THUẬT TOÁN PLAYFAIR & LOGIC CODE

## 1. 🌟 TỔNG QUAN
Chương trình Playfair Cipher này hỗ trợ mã hóa và giải mã văn bản dựa trên ma trận khóa. Điểm đặc biệt của phiên bản này là khả năng tùy chỉnh ký tự chèn (Separator) và hỗ trợ xử lý Unicode thông minh (bỏ qua ký tự có dấu).

Chương trình hỗ trợ 2 chế độ ma trận:
* **Chế độ 5x5:** Dùng 25 chữ cái (A-Z), trong đó **I** và **J** được gộp thành một.
* **Chế độ 6x6:** Dùng 36 ký tự (A-Z và 0-9).

---

## 2. 🧩 TẠO MA TRẬN KHÓA (Matrix Generation)

Hàm `generate_matrix` chịu trách nhiệm tạo bảng mã từ khóa đầu vào (Key).

### A. Quy trình tạo ma trận 5x5
1.  **Xử lý Key:**
    * Chuyển toàn bộ về chữ in hoa.
    * Loại bỏ các ký tự không phải chữ cái (A-Z).
    * Thay thế mọi chữ `J` thành `I`.
2.  **Tạo chuỗi duy nhất:** Giữ lại các ký tự xuất hiện lần đầu tiên trong Key (loại bỏ trùng lặp).
3.  **Điền đầy ma trận:**
    * Điền các ký tự từ Key vào trước.
    * Điền nốt các chữ cái còn thiếu trong bảng chữ cái (A-Z, trừ J) vào sau.
4.  **Cắt ma trận:** Chia chuỗi thành 5 hàng x 5 cột.

### B. Quy trình tạo ma trận 6x6
* Tương tự như 5x5 nhưng sử dụng bộ ký tự `A-Z` và `0-9`.
* Không cần gộp I và J.
* Ma trận có kích thước 6 hàng x 6 cột.

---

## 3. 📝 XỬ LÝ VĂN BẢN ĐẦU VÀO (Preprocessing)

Trước khi mã hóa hoặc giải mã, văn bản cần được chuẩn hóa và chia thành các cặp ký tự (Digraphs).

### A. Lọc ký tự (Strict ASCII Filter)
Chương trình sử dụng bộ lọc nghiêm ngặt để đảm bảo tính chính xác:
* Chỉ giữ lại các ký tự ASCII chuẩn (A-Z cho 5x5, A-Z/0-9 cho 6x6).
* **Ký tự có dấu (Tiếng Việt):** Sẽ được coi là ký tự đặc biệt và **không tham gia** vào quá trình tạo cặp (chúng được giữ nguyên vị trí trong kết quả cuối cùng).

### B. Quy tắc chèn ký tự phân tách (Separators)
Người dùng có thể tùy chỉnh 2 ký tự phân tách (gọi là `Sep1` và `Sep2`. Mặc định là `X` và `Y`).

Hàm `process_plaintext` duyệt qua văn bản và chia cặp như sau:
1.  **Nếu 2 ký tự trong cặp giống nhau (VD: AA):**
    * Chèn ký tự phân tách vào giữa.
    * Nếu ký tự bị trùng là `Sep1` ➡️ Chèn `Sep2`. (VD: `XX` -> `XY X...`)
    * Nếu ký tự bị trùng KHÁC `Sep1` ➡️ Chèn `Sep1`. (VD: `AA` -> `AX A...`)
2.  **Nếu ký tự khác nhau:** Tạo thành 1 cặp bình thường.
3.  **Xử lý ký tự lẻ:** Nếu cuối cùng còn dư 1 ký tự, chèn thêm `Sep1` (hoặc `Sep2` nếu ký tự cuối trùng `Sep1`) để đủ cặp.

---

## 4. 🔒 QUY TẮC MÃ HÓA & GIẢI MÃ (Core Logic)

Dựa vào vị trí dòng (`row`) và cột (`col`) của cặp ký tự `(a, b)` trong ma trận:

### Trường hợp 1: Cùng Dòng (Same Row)
* **Mã hóa:** Lấy ký tự bên **PHẢI** `(col + 1)`.
* **Giải mã:** Lấy ký tự bên **TRÁI** `(col - 1)`.
* *Lưu ý:* Nếu đi ra khỏi biên thì vòng lại đầu/cuối dòng.

### Trường hợp 2: Cùng Cột (Same Column)
* **Mã hóa:** Lấy ký tự bên **DƯỚI** `(row + 1)`.
* **Giải mã:** Lấy ký tự bên **TRÊN** `(row - 1)`.
* *Lưu ý:* Nếu đi ra khỏi biên thì vòng lại đầu/cuối cột.

### Trường hợp 3: Hình Chữ Nhật (Rectangle)
* **Mã hóa & Giải mã:** Giữ nguyên dòng, **hoán đổi cột** cho nhau.
    * Ký tự mới của `a`: Giao điểm dòng `a` và cột `b`.
    * Ký tự mới của `b`: Giao điểm dòng `b` và cột `a`.

---

## 5. 🛠️ TÁI TẠO VĂN BẢN (Reconstruction)

Sau khi có chuỗi kết quả từ thuật toán (chỉ gồm các ký tự in hoa liền nhau), chương trình thực hiện bước "Reconstruct" để trả về định dạng giống hệt văn bản gốc:

1.  Duyệt lại từng ký tự trong văn bản gốc (`input_text`).
2.  **Nếu là ký tự hợp lệ (đã được mã hóa):**
    * Lấy ký tự tương ứng từ chuỗi kết quả.
    * Khôi phục định dạng Hoa/Thường (Upper/Lower) dựa theo ký tự gốc.
    * Nếu tại vị trí đó có chèn thêm Separator (do bước Preprocessing), chương trình sẽ tự động chèn separator đó vào kết quả.
3.  **Nếu là ký tự đặc biệt/có dấu:**
    * Giữ nguyên ký tự đó tại vị trí cũ.

>### 💡 VÍ DỤ MINH HỌA (Đúng với Code)
>
>Giả sử Sep1="X", Sep2="Y". Ma trận 5x5.
>
>**Trường hợp 1: Input tiếng Anh (Có cặp trùng)**
>* **Input:** `HELLO`
>* **Pre-process:** `HE` `LL` (trùng L) → tách thành `HE LX LO`
>* **Mã hóa:** Giả sử `HE`->`KC`, `LX`->`RV`, `LO`->`QA`
>* **Output:** `KCRVQA`
>
>**Trường hợp 2: Input tiếng Việt có dấu**
>* **Input:** `Hế lô`
>* **Phân tích:**
>    * `H`: Hợp lệ.
>    * `ế`: Không hợp lệ (Bỏ qua).
>    * ` ` (cách): Không hợp lệ (Bỏ qua).
>    * `l`: Hợp lệ.
>    * `ô`: Không hợp lệ (Bỏ qua).
>* **Pre-process:** Chỉ còn chuỗi `Hl` → cặp `HL`.
>* **Mã hóa cặp HL:** Giả sử ra `AB`.
>* **Reconstruct (Ghép lại):**
>    * `H` → thay bằng `A`.
>    * `ế` → giữ nguyên `ế`.
>    * ` ` → giữ nguyên ` `.
>    * `l` → thay bằng `b` (viết thường theo gốc).
>    * `ô` → giữ nguyên `ô`.
>* **Output:** `Aế bô`

---

## 6. ⚠️ LƯU Ý QUAN TRỌNG
1.  **Giải mã:** Kết quả giải mã sẽ **VẪN CHỨA** các ký tự phân tách (`Sep1`, `Sep2`) nếu chúng được chèn vào lúc mã hóa. Đây là đặc điểm của thuật toán Playfair, người đọc cần tự loại bỏ các ký tự thừa này để hiểu nội dung gốc.
2.  **Toàn vẹn dữ liệu:** Do cơ chế bỏ qua ký tự lạ, văn bản sau khi giải mã sẽ bảo toàn được cấu trúc câu, dấu câu và các ký tự Tiếng Việt có dấu của văn bản gốc.