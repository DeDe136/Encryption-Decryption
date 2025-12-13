import customtkinter as ctk
from tkinter import messagebox
import os

class ExplanationViewer(ctk.CTkToplevel):
    """Cửa sổ hiển thị giải thích thuật toán"""
    
    def __init__(self, parent, algorithm_name):
        super().__init__(parent)
        
        self.algorithm_name = algorithm_name
        
        # Cấu hình cửa sổ
        self.title(f"Giải thích: {algorithm_name}")
        self.geometry("900x700")
        
        # Không cho resize quá nhỏ
        self.minsize(700, 500)
        
        # Tạo giao diện
        self.create_widgets()
        
        # Load nội dung
        self.load_explanation()
        
        # Focus vào cửa sổ này
        self.focus()
    
    def create_widgets(self):
        """Tạo các widgets"""
        
        # Header
        header_frame = ctk.CTkFrame(self, height=80, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Title với icon
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"📚 {self.algorithm_name}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", pady=10)
        
        # Button frame (bên phải header)
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        # Nút Close
        close_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Đóng",
            width=100,
            command=self.destroy,
            fg_color="gray30",
            hover_color="gray20"
        )
        close_btn.pack()
        
        # Separator
        separator = ctk.CTkFrame(self, height=2, fg_color="gray40")
        separator.pack(fill="x", padx=20, pady=5)
        
        # Main content frame với scrollbar
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Textbox với scrollbar
        self.text_widget = ctk.CTkTextbox(
            content_frame,
            wrap="word",
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="gray15"
        )
        self.text_widget.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Footer với thông tin
        footer = ctk.CTkLabel(
            self,
            text="💡 Tip: Cuộn để xem toàn bộ nội dung giải thích",
            font=ctk.CTkFont(size=11),
            text_color="gray50"
        )
        footer.pack(pady=(5, 15))
    
    def load_explanation(self):
        """Load file giải thích tương ứng"""
        
        # Mapping tên thuật toán → file path
        # LƯU Ý: Đảm bảo bạn đã tạo các file .md này trong thư mục dự án
        explanations = {
            "Caesar Cipher": "algorithms/caesar/explanation.md",
            "Monoalphabetic Substitution": "algorithms/monoalphabetic/explanation.md",
            "Vigenère Cipher": "algorithms/vigenere/explanation.md",
            "DES": "algorithms/des/explanation.md",
            "AES": "algorithms/aes/explanation.md"
        }
        
        filepath = explanations.get(self.algorithm_name)
        
        if not filepath:
            self.text_widget.insert("1.0", f"❌ Không tìm thấy giải thích cho {self.algorithm_name}")
            return
        
        # Đọc file
        try:
            # Get absolute path
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # Nếu file này nằm cùng cấp với main.py thì dùng:
            # base_dir = os.path.dirname(os.path.abspath(__file__))
            
            full_path = os.path.join(base_dir, filepath)
            
            # Kiểm tra xem file có tồn tại không trước khi mở
            if not os.path.exists(full_path):
                 # Fallback thử tìm đường dẫn tương đối nếu chạy trực tiếp
                if os.path.exists(filepath):
                    full_path = filepath
                else:
                    raise FileNotFoundError(f"Path not found: {full_path}")

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Hiển thị và format
            self.apply_formatting(content)
            
            # Scroll to top
            self.text_widget.see("1.0")
            
        except FileNotFoundError:
            self.text_widget.insert("1.0", f"❌ File không tồn tại: {filepath}\n\nVui lòng tạo file giải thích.")
        except Exception as e:
            self.text_widget.insert("1.0", f"❌ Lỗi khi đọc file: {str(e)}")
            # messagebox.showerror("Lỗi", f"Không thể đọc file: {str(e)}") # Optional

    def apply_formatting(self, content):
        """
        Apply basic formatting cho markdown.
        FIX: Sử dụng ._textbox để config tag và dùng tuple font chuẩn
        """
        # Xóa text hiện tại
        self.text_widget.delete("1.0", "end")
        
        # --- PHẦN SỬA LỖI QUAN TRỌNG ---
        # Truy cập vào widget gốc của Tkinter bên trong CTkTextbox
        tk_text = self.text_widget._textbox 
        
        # Định nghĩa font bằng tuple chuẩn (Font-family, Size, Style)
        # Thay vì dùng ctk.CTkFont gây lỗi scaling
        tk_text.tag_config("h1", font=("Roboto", 20, "bold"), foreground="#4A9EFF")
        tk_text.tag_config("h2", font=("Roboto", 18, "bold"), foreground="#66B3FF")
        tk_text.tag_config("h3", font=("Roboto", 16, "bold"), foreground="#80C4FF")
        tk_text.tag_config("h4", font=("Roboto", 14, "bold"), foreground="#99D5FF")
        tk_text.tag_config("code", font=("Consolas", 12, "normal"), background="#2B2B2B") # gray20 hex
        tk_text.tag_config("bold", font=("Roboto", 13, "bold"))
        # -------------------------------
        
        lines = content.split("\n")
        in_code_block = False
        
        for line in lines:
            # Check for code blocks
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue
            
            # Inside code block
            if in_code_block:
                self.text_widget.insert("end", line + "\n", "code")
                continue
            
            # Headings
            if line.startswith("# "):
                self.text_widget.insert("end", line[2:] + "\n", "h1")
            elif line.startswith("## "):
                self.text_widget.insert("end", line[3:] + "\n", "h2")
            elif line.startswith("### "):
                self.text_widget.insert("end", line[4:] + "\n", "h3")
            elif line.startswith("#### "):
                self.text_widget.insert("end", line[5:] + "\n", "h4")
            
            # Bold text **text** (Simple parser)
            elif "**" in line:
                parts = line.split("**")
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        self.text_widget.insert("end", part)
                    else:
                        self.text_widget.insert("end", part, "bold")
                self.text_widget.insert("end", "\n")
            
            # Inline code `code` (Simple parser)
            elif "`" in line and not line.strip().startswith("`"):
                parts = line.split("`")
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        self.text_widget.insert("end", part)
                    else:
                        self.text_widget.insert("end", part, "code")
                self.text_widget.insert("end", "\n")
            
            # Normal line
            else:
                self.text_widget.insert("end", line + "\n")