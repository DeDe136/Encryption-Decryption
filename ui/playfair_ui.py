import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QRadioButton,
    QButtonGroup, QFileDialog, QGridLayout, QFrame,
    QMessageBox, QStackedWidget, QGraphicsDropShadowEffect, QSizePolicy, QDialog, QScrollArea
)
from PyQt5.QtCore import Qt, QRegExp, QEvent
from PyQt5.QtGui import QFont, QColor, QCursor, QRegExpValidator

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --- IMPORT LOGIC ---
from algorithms.playfair import playfair_cipher as pc

class InfoDialog(QDialog):
    # ... (Giữ nguyên code InfoDialog của bạn) ...
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📘 Giải thích thuật toán Playfair")
        self.resize(1150, 850)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        self.setStyleSheet("background-color: #f3f4f6;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header_container = QFrame()
        header_container.setStyleSheet("background-color: white; border-bottom: 1px solid #e5e7eb;")
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(30, 25, 30, 25)
        
        title = QLabel("💡 Nguyên lý hoạt động & Logic Code")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #111827; border: none;")
        header_layout.addWidget(title)
        layout.addWidget(header_container)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: none;
                padding: 40px;
                background-color: white;
                color: #374151;
                font-family: 'Segoe UI', 'Verdana', sans-serif;
                font-size: 25px;
                line-height: 4.0;
            }
            QScrollBar:vertical { border: none; background: #f1f5f9; width: 14px; margin: 0px; }
            QScrollBar::handle:vertical { background-color: #cbd5e1; min-height: 30px; border-radius: 4px; margin: 3px; }
            QScrollBar::handle:vertical:hover { background-color: #94a3b8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)
        
        layout.addWidget(self.text_edit)
        
        footer_container = QFrame()
        footer_container.setStyleSheet("background-color: #f9fafb; border-top: 1px solid #e5e7eb;")
        footer_layout = QHBoxLayout(footer_container)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        footer_layout.addStretch()
        
        btn_close = QPushButton("Close")
        btn_close.setCursor(QCursor(Qt.PointingHandCursor))
        btn_close.setFixedSize(140, 50)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #4b5563; color: white; font-weight: 600; font-size: 18px;
                border-radius: 8px; border: none;
            }
            QPushButton:hover { background-color: #374151; }
        """)
        btn_close.clicked.connect(self.close)
        footer_layout.addWidget(btn_close)
        
        layout.addWidget(footer_container)
        self.setLayout(layout)
        self.load_content()

    def load_content(self):
        file_name = "explanation.md"
        try:
            current_ui_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_ui_dir)
            file_path = os.path.join(project_root, 'algorithms', 'playfair', file_name)
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_edit.setMarkdown(content)
            else:
                self.text_edit.setMarkdown(f"# ⚠️ Lỗi\nKhông tìm thấy file tại: `{file_path}`")
        except Exception as e:
            self.text_edit.setText(f"Lỗi: {str(e)}")

class ModernPlayfairUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Playfair Cipher - Encrypt & Decrypt")
        self.setGeometry(100, 50, 1200, 700) 
        
        # State
        self.matrix = []
        self.matrix_size = '5'
        self.mode = 'encrypt'
        self.input_mode = 'file' 
        self.input_file_content = ''
        self.file_path = ''

        self.init_ui()
        self.setup_connections()
        self.update_input_tab_style()
        self.update_key_validator()
        self.update_labels()
        self.generate_and_show_matrix()

    def init_ui(self):
        # ... (Giữ nguyên toàn bộ phần setup giao diện của bạn) ...
        self.setStyleSheet("background-color: #e5e7eb; font-family: 'Segoe UI', sans-serif;")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # --- MAIN CARD ---
        self.card = QFrame()
        self.card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.card.setGraphicsEffect(shadow)
        main_layout.addWidget(self.card)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(10)

        # Header
        header = QLabel("Playfair Cipher - Encrypt & Decrypt")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1f2937; margin-bottom: 5px; border: none;")
        card_layout.addWidget(header)

        # Content Grid
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        card_layout.addLayout(content_layout)

        # ================= LEFT PANEL =================
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        content_layout.addLayout(left_panel, 3) 

        # 1. Separators
        sep_container = QHBoxLayout()
        sep_container.setSpacing(15)
        
        # --- [THÊM] Validator chỉ cho phép nhập chữ cái (A-Z) ---
        sep_validator = QRegExpValidator(QRegExp("[A-Za-z]"))

        sep1_layout = QVBoxLayout()
        label_sep1 = QLabel("First Separator:")
        label_sep1.setStyleSheet("font-weight: 600; color: #374151; border: none; background: transparent;")
        self.inp_sep1 = QLineEdit("X")
        self.inp_sep1.setMaxLength(1)
        self.inp_sep1.setValidator(sep_validator) # [THÊM] Áp dụng validator
        self.style_input(self.inp_sep1)
        # [THÊM] Sự kiện khi nhập: Tự in hoa và kiểm tra trùng
        self.inp_sep1.textEdited.connect(lambda t: self.handle_separator(self.inp_sep1, self.inp_sep2, t))

        sep1_layout.addWidget(label_sep1)
        sep1_layout.addWidget(self.inp_sep1)
        
        sep2_layout = QVBoxLayout()
        label_sep2 = QLabel("Second Separator:")
        label_sep2.setStyleSheet("font-weight: 600; color: #374151; border: none; background: transparent;")
        self.inp_sep2 = QLineEdit("Y")
        self.inp_sep2.setMaxLength(1)
        self.inp_sep2.setValidator(sep_validator) # [THÊM] Áp dụng validator
        self.style_input(self.inp_sep2)
        # [THÊM] Sự kiện khi nhập: Tự in hoa và kiểm tra trùng
        self.inp_sep2.textEdited.connect(lambda t: self.handle_separator(self.inp_sep2, self.inp_sep1, t))

        sep2_layout.addWidget(label_sep2)
        sep2_layout.addWidget(self.inp_sep2)

        sep_container.addLayout(sep1_layout)
        sep_container.addLayout(sep2_layout)
        left_panel.addLayout(sep_container)

        # 2. Key Input
        key_label = QLabel("Key:")
        key_label.setStyleSheet("font-weight: 600; color: #374151; border: none; background: transparent;")
        self.inp_key = QLineEdit()
        self.style_input(self.inp_key)
        self.inp_key.setPlaceholderText("Enter key...")
        left_panel.addWidget(key_label)
        left_panel.addWidget(self.inp_key)

        # 3. Matrix Area
        matrix_area_layout = QHBoxLayout()
        
        self.matrix_frame = QFrame()
        self.matrix_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: #f9fafb; 
                padding: 10px;
            }
        """)
        self.matrix_grid_layout = QVBoxLayout(self.matrix_frame)
        
        matrix_title = QLabel("Matrix:")
        matrix_title.setStyleSheet("font-size: 17px; font-weight: 600; color: #374151; border: none; margin-bottom: 5px; background: transparent;")
        self.matrix_grid_layout.addWidget(matrix_title)

        self.grid_container = QGridLayout()
        self.grid_container.setSpacing(5)
        self.grid_container.setAlignment(Qt.AlignCenter)
        self.matrix_grid_layout.addLayout(self.grid_container)
        
        size_layout = QVBoxLayout()
        size_layout.addWidget(self.create_label("Size:", 17))
        
        self.radio_5x5 = QRadioButton("5x5")
        self.radio_6x6 = QRadioButton("6x6")
        self.radio_5x5.setChecked(True)
        self.style_radio(self.radio_5x5)
        self.style_radio(self.radio_6x6)
        
        self.size_group = QButtonGroup()
        self.size_group.addButton(self.radio_5x5, 5)
        self.size_group.addButton(self.radio_6x6, 6)

        size_layout.addWidget(self.radio_5x5)
        size_layout.addWidget(self.radio_6x6)
        size_layout.addStretch()

        matrix_area_layout.addWidget(self.matrix_frame, 1)
        matrix_area_layout.addLayout(size_layout)
        
        left_panel.addLayout(matrix_area_layout)

        # 4. Mode Selection
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("font-weight: 600; color: #374151; border: none; background: transparent;")
        left_panel.addWidget(mode_label)

        mode_radios = QHBoxLayout()
        self.radio_encrypt = QRadioButton("Encrypt")
        self.radio_decrypt = QRadioButton("Decrypt")
        self.radio_encrypt.setChecked(True)
        self.style_radio(self.radio_encrypt)
        self.style_radio(self.radio_decrypt)

        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.radio_encrypt)
        self.mode_group.addButton(self.radio_decrypt)

        mode_radios.addWidget(self.radio_encrypt)
        mode_radios.addWidget(self.radio_decrypt)
        mode_radios.addStretch()
        left_panel.addLayout(mode_radios)

        left_panel.addStretch()

        # 5. Buttons
        self.btn_run = self.create_button("▶ Excute", "#16a34a", "#15803d")
        self.btn_clear = self.create_button("🗑 Clear All", "#ef4444", "#dc2626")
        self.btn_cancel_left = self.create_button("← Cancel", "#6b7280", "#4b5563")

        left_panel.addWidget(self.btn_run)
        left_panel.addWidget(self.btn_clear)
        left_panel.addWidget(self.btn_cancel_left)

        # ================= RIGHT PANEL =================
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        content_layout.addLayout(right_panel, 7)

        # --- GROUP INPUT ---
        input_section_layout = QVBoxLayout()
        input_section_layout.setSpacing(5)

        # 1. Tabs
        tab_header_layout = QHBoxLayout()
        tab_header_layout.setSpacing(15)
        
        self.btn_tab_file = QPushButton("File Input")
        self.btn_tab_text = QPushButton("Text Input")
        self.btn_tab_file.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_tab_text.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_tab_file.setFixedHeight(38)
        self.btn_tab_text.setFixedHeight(38)
        
        tab_header_layout.addWidget(self.btn_tab_file)
        tab_header_layout.addWidget(self.btn_tab_text)
        tab_header_layout.addStretch()
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #e5e7eb; background: transparent;")

        input_section_layout.addLayout(tab_header_layout)
        input_section_layout.addWidget(line)

        # 2. Input Content
        self.input_stack = QStackedWidget()
        self.input_stack.setStyleSheet("background-color: transparent;") 
        
        # --- File Input Page ---
        page_file = QWidget()
        page_file.setStyleSheet("background-color: transparent;")
        
        page_file_layout = QVBoxLayout(page_file)
        page_file_layout.setContentsMargins(0, 5, 0, 0)
        page_file_layout.setSpacing(5)

        lbl_path = QLabel("Path:")
        lbl_path.setStyleSheet("font-size: 20px; font-weight: 600; color: #374151; border: none; background: transparent;")
        page_file_layout.addWidget(lbl_path)

        # Row: Input + Button
        file_row_layout = QHBoxLayout()
        file_row_layout.setSpacing(10)

        self.inp_file_display = QLineEdit()
        self.inp_file_display.setReadOnly(True)
        self.inp_file_display.setPlaceholderText("Select input file...")
        self.inp_file_display.setStyleSheet("""
            QLineEdit {
                background-color: #f9fafb; 
                border: 1px solid #d1d5db;
                border-radius: 6px; padding: 6px 8px; color: #374151;
            }
        """)
        
        self.btn_browse = self.create_button("Browse", "#a16207", "#854d0e")
        self.btn_browse.setFixedSize(100, 44) # Giữ kích thước nhỏ cho nút browse

        file_row_layout.addWidget(self.inp_file_display)
        file_row_layout.addWidget(self.btn_browse)
        
        page_file_layout.addLayout(file_row_layout)
        page_file_layout.addStretch()
        
        # --- Text Input Page ---
        page_text = QWidget()
        page_text.setStyleSheet("background-color: transparent;")
        page_text_layout = QVBoxLayout(page_text)
        page_text_layout.setContentsMargins(0, 5, 0, 0)
        page_text_layout.setSpacing(5)
        
        lbl_text = QLabel("Text:")
        lbl_text.setStyleSheet("font-size: 20px; font-weight: 600; color: #374151; border: none; background: transparent;")
        page_text_layout.addWidget(lbl_text)

        self.inp_text_area = QTextEdit()
        self.inp_text_area.setPlaceholderText("Enter text here...")
        self.style_textarea(self.inp_text_area, read_only=False)
        self.inp_text_area.setFixedHeight(80)
        page_text_layout.addWidget(self.inp_text_area)
        page_text_layout.addStretch()

        self.input_stack.addWidget(page_file)
        self.input_stack.addWidget(page_text)
        input_section_layout.addWidget(self.input_stack)

        right_panel.addLayout(input_section_layout)

        # 3. Output
        label_output_style = "font-size: 20px; font-weight: 600; color: #374151; border: none; background: transparent; margin-top: 5px;"

        self.lbl_pairs = QLabel()
        self.lbl_pairs.setStyleSheet(label_output_style)
        self.out_pairs = QTextEdit()
        self.style_textarea(self.out_pairs, read_only=True)
        
        self.lbl_stream = QLabel()
        self.lbl_stream.setStyleSheet(label_output_style)
        self.out_stream = QTextEdit()
        self.style_textarea(self.out_stream, read_only=True)
        
        self.lbl_result = QLabel()
        self.lbl_result.setStyleSheet(label_output_style)
        self.out_result = QTextEdit()
        self.style_textarea(self.out_result, read_only=True)
        self.out_result.setFixedHeight(130)

        right_panel.addWidget(self.lbl_pairs)
        right_panel.addWidget(self.out_pairs)
        right_panel.addWidget(self.lbl_stream)
        right_panel.addWidget(self.out_stream)
        right_panel.addWidget(self.lbl_result)
        right_panel.addWidget(self.out_result)

        # 4. Buttons Right
        bottom_btns = QHBoxLayout()
        self.btn_save = self.create_button("💾 Save", "#2563eb", "#1d4ed8")
        self.btn_info = self.create_button("💡 Learn Algorithm", "#efb114", "#d97706")

        bottom_btns.addWidget(self.btn_save)
        bottom_btns.addWidget(self.btn_info)
        right_panel.addLayout(bottom_btns)

    # --- HELPERS ĐỂ CODE GỌN HƠN ---
    def create_label(self, text, size=None):
        lbl = QLabel(text)
        s = f"font-weight: 600; color: #374151; border: none; background: transparent;"
        if size: s += f" font-size: {size}px;"
        lbl.setStyleSheet(s)
        return lbl

    def create_button(self, text, color, hover):
        btn = QPushButton(text)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setStyleSheet(f"""
            QPushButton {{ background-color: {color}; color: white; font-weight: bold; border-radius: 6px; padding: 10px; border: none; }}
            QPushButton:hover {{ background-color: {hover}; }}
        """)
        return btn

    # --- SỰ KIỆN CHUỘT ---
    def mousePressEvent(self, event):
        focused_widget = QApplication.focusWidget()
        if focused_widget:
            focused_widget.clearFocus()
        super().mousePressEvent(event)

    # --- STYLING ---
    def style_input(self, widget):
        widget.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db; border-radius: 6px;
                padding: 6px 12px; color: #1f2937; background-color: white;
            }
            QLineEdit:focus { border: 2px solid #3b82f6; padding: 5px 11px; }
        """)

    def style_textarea(self, widget, read_only=False):
        bg_color = "#f9fafb" if read_only else "white"
        widget.setReadOnly(read_only)
        widget.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid #d1d5db; border-radius: 6px;
                padding: 6px; color: #1f2937; background-color: {bg_color};
                font-family: 'Consolas', monospace;
            }}
            QTextEdit:focus {{ border: 2px solid #3b82f6; }}
            QScrollBar:vertical {{ border: none; background-color: transparent; width: 8px; margin: 0px; }}
            QScrollBar::handle:vertical {{ background-color: #cbd5e1; border-radius: 4px; min-height: 20px; }}
            QScrollBar::handle:vertical:hover {{ background-color: #94a3b8; }}
        """)

    def style_radio(self, widget):
        widget.setStyleSheet("""
            QRadioButton { color: #374151; spacing: 8px; font-size: 17px; background-color: transparent; }
            QRadioButton::indicator { width: 16px; height: 16px; }
        """)

    def update_input_tab_style(self):
        active_style = """
            QPushButton {
                color: #2563eb; font-weight: bold; border: none;
                border-bottom: 2px solid #2563eb; background-color: transparent;
                font-size: 20px; padding-bottom: 5px;
            }
        """
        inactive_style = """
            QPushButton {
                color: #4b5563; font-weight: normal; border: none;
                border-bottom: 2px solid transparent; background-color: transparent;
                font-size: 20px; padding-bottom: 5px;
            }
            QPushButton:hover { color: #1f2937; }
        """
        if self.input_mode == 'file':
            self.btn_tab_file.setStyleSheet(active_style)
            self.btn_tab_text.setStyleSheet(inactive_style)
            self.input_stack.setCurrentIndex(0)
        else:
            self.btn_tab_file.setStyleSheet(inactive_style)
            self.btn_tab_text.setStyleSheet(active_style)
            self.input_stack.setCurrentIndex(1)

    def update_labels(self):
        if self.radio_encrypt.isChecked():
            self.lbl_pairs.setText("Plaintext Pairs:")
            self.lbl_stream.setText("Ciphertext Stream:")
            self.lbl_result.setText("Encryption Result:")
        else:
            self.lbl_pairs.setText("Ciphertext Pairs:")
            self.lbl_stream.setText("Plaintext Stream:")
            self.lbl_result.setText("Decryption Result:")

    def render_matrix(self, matrix_data):
        for i in reversed(range(self.grid_container.count())): 
            self.grid_container.itemAt(i).widget().setParent(None)
            
        if not matrix_data:
            return

        for r, row in enumerate(matrix_data):
            for c, char in enumerate(row):
                cell = QLabel(char)
                cell.setFixedSize(40, 40)
                cell.setAlignment(Qt.AlignCenter)
                cell.setStyleSheet("""
                    QLabel {
                        background-color: white;
                        border: 1px solid #d1d5db;
                        color: #1f2937;
                        font-family: 'Consolas', monospace;
                        font-weight: bold;
                        border-radius: 4px;
                    }
                """)
                self.grid_container.addWidget(cell, r, c)

    # --- LOGIC HANDLERS ---
    def setup_connections(self):
        self.inp_key.textEdited.connect(self.on_key_edited)
        self.size_group.buttonClicked.connect(self.on_size_change)
        self.mode_group.buttonClicked.connect(self.update_labels)
        
        self.btn_tab_file.clicked.connect(lambda: self.switch_tab('file'))
        self.btn_tab_text.clicked.connect(lambda: self.switch_tab('text'))
        self.btn_browse.clicked.connect(self.browse_file)
        self.btn_run.clicked.connect(self.run_cipher)
        self.btn_clear.clicked.connect(self.clear_all_inputs)
        self.btn_cancel_left.clicked.connect(self.close)
        self.btn_info.clicked.connect(self.show_info)
        self.btn_save.clicked.connect(self.save_file)

    # --- [THÊM HÀM MỚI] Xử lý logic Separator ---
    def handle_separator(self, current, other, text):
        if not text: return
        
        # Tự động viết hoa
        upper_text = text.upper()
        if text != upper_text:
            current.setText(upper_text)
        
        # Kiểm tra trùng với ô kia
        if upper_text == other.text():
            QMessageBox.warning(self, "Lỗi", "Hai ký tự Separator không được giống nhau!")
            current.setText("") # Xóa ký tự vừa nhập nếu trùng

    def update_key_validator(self):
        key_text = self.inp_key.text()
        if self.matrix_size == '5':
            # Dùng regex chỉ cho ASCII
            regex = QRegExp("[A-Za-z]+")
            validator = QRegExpValidator(regex)
            self.inp_key.setValidator(validator)
            # Lọc lại text hiện có bằng logic ASCII
            cleaned = ''.join(c for c in key_text if pc.is_ascii_letter(c))
            if cleaned != key_text:
                self.inp_key.setText(cleaned)
        else:
            regex = QRegExp("[A-Za-z0-9]+")
            validator = QRegExpValidator(regex)
            self.inp_key.setValidator(validator)
            cleaned = ''.join(c for c in key_text if pc.is_ascii_alnum(c))
            if cleaned != key_text:
                self.inp_key.setText(cleaned)

    def on_key_edited(self, text):
        upper_text = text.upper()
        if text != upper_text:
            self.inp_key.setText(upper_text)
        self.generate_and_show_matrix()

    def on_size_change(self, btn):
        self.matrix_size = str(self.size_group.id(btn))
        self.update_key_validator()
        self.generate_and_show_matrix()

    def generate_and_show_matrix(self):
        key = self.inp_key.text()
        # Gọi hàm từ module pc
        if self.matrix_size == '5':
            self.matrix = pc.generate_matrix_5x5(key)
        else:
            self.matrix = pc.generate_matrix_6x6(key)
        self.render_matrix(self.matrix)

    def switch_tab(self, mode):
        self.input_mode = mode
        self.update_input_tab_style()

    def browse_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '', "Text files (*.txt)")
        if fname:
            self.file_path = fname
            self.inp_file_display.setText(fname)
            try:
                with open(fname, 'r', encoding='utf-8') as f:
                    self.input_file_content = f.read()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not read file: {e}")

    # === PHẦN QUAN TRỌNG: CẬP NHẬT LOGIC RUN CIPHER ĐỂ BỎ QUA DẤU ===
    def run_cipher(self):
        if not self.matrix:
             QMessageBox.warning(self, "Warning", "Error creating matrix!")
             return
        
        # 1. Lấy giá trị Separator từ UI
        sep1 = self.inp_sep1.text()
        sep2 = self.inp_sep2.text()

        # Kiểm tra tính hợp lệ
        if not sep1 or not sep2:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đủ ký tự cho cả 2 Separator!")
            return
        if sep1 == sep2:
            QMessageBox.warning(self, "Lỗi", "Hai Separator không được giống nhau!")
            return

        input_text = ""
        if self.input_mode == 'file':
            input_text = self.input_file_content
            if not input_text and not self.file_path:
                QMessageBox.warning(self, "Warning", "Please select a file!")
                return
        else:
            input_text = self.inp_text_area.toPlainText()
            if not input_text:
                QMessageBox.warning(self, "Warning", "Please enter text!")
                return
        
        mode = 'encrypt' if self.radio_encrypt.isChecked() else 'decrypt'
        
        try:
            # --- LOGIC XỬ LÝ CHUNG CHO CẢ 2 CHẾ ĐỘ ---
            # Bây giờ cả Encrypt và Decrypt đều dùng process_plaintext để chèn Separator
            if self.matrix_size == '5':
                pairs, inserted_indices = pc.process_plaintext_5x5(input_text, sep1=sep1, sep2=sep2)
            else:
                pairs, inserted_indices = pc.process_plaintext_6x6(input_text, sep1=sep1, sep2=sep2)
            
            self.out_pairs.setText(' '.join(pairs))
            
            processed_pairs = []
            for pair in pairs:
                if len(pair) == 2:
                    if mode == 'encrypt':
                        # Nếu là mã hóa thì dùng encrypt_pair
                        processed_pairs.append(pc.encrypt_pair(self.matrix, pair[0], pair[1]))
                    else:
                        # Nếu là giải mã thì dùng decrypt_pair
                        processed_pairs.append(pc.decrypt_pair(self.matrix, pair[0], pair[1]))
            
            output_stream = ''.join(processed_pairs)
            self.out_stream.setText(' '.join(processed_pairs))
            
            # --- RECONSTRUCT (Tái tạo lại chuỗi kết quả giữ nguyên format gốc) ---
            # Logic này giờ áp dụng cho cả Encrypt và Decrypt
            result = []
            idx = 0
            for char in input_text:
                is_valid = pc.is_ascii_letter(char) if self.matrix_size == '5' else pc.is_ascii_alnum(char)
                
                if is_valid:
                    if idx < len(output_stream):
                        c = output_stream[idx]
                        result.append(c.lower() if char.islower() else c)
                        idx += 1
                        # Nếu vị trí này là vị trí đã chèn separator, ta lấy tiếp ký tự từ stream
                        while idx in inserted_indices and idx < len(output_stream):
                            result.append(output_stream[idx])
                            idx += 1
                else:
                    # Giữ nguyên ký tự có dấu/đặc biệt
                    result.append(char)
            
            # Thêm nốt các ký tự còn dư trong stream (nếu có)
            while idx < len(output_stream):
                result.append(output_stream[idx])
                idx += 1
                
            self.out_result.setText(''.join(result))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def clear_all(self):
        self.out_pairs.clear()
        self.out_stream.clear()
        self.out_result.clear()
        
    def clear_all_inputs(self):
        self.inp_text_area.clear()
        self.inp_file_display.clear()
        self.input_file_content = ''
        self.file_path = ''
        self.clear_all()

    def show_info(self):
        dialog = InfoDialog(self)
        dialog.exec_()

    def save_file(self):
        content = self.out_result.toPlainText()
        if not content:
            QMessageBox.warning(self, "Warning", "No result to save!")
            return
        fname, _ = QFileDialog.getSaveFileName(self, 'Save file', 'result.txt', "Text files (*.txt)")
        if fname:
            try:
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = ModernPlayfairUI()
    window.show()
    sys.exit(app.exec_())