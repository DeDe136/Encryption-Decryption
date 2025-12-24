import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QRadioButton,
    QButtonGroup, QFileDialog, QFrame, QMessageBox, 
    QStackedWidget, QGraphicsDropShadowEffect, QComboBox,
    QScrollArea
)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QFont, QColor, QCursor, QPainter, QPen, QBrush, QPolygonF

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64

class CustomComboBox(QComboBox):
    def paintEvent(self, event):
        super().paintEvent(event)
        # Vẽ mũi tên hiện đại
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Tọa độ và kích thước mũi tên
        arrow_x = self.width() - 20
        arrow_y = self.height() // 2
        
        # Vẽ mũi tên hiện đại (tam giác nhỏ)
        painter.setPen(QPen(QColor("#6b7280"), 2))
        painter.setBrush(QBrush(QColor("#6b7280")))
        
        # Tạo hình tam giác bằng QPolygonF
        polygon = QPolygonF()
        polygon.append(QPointF(arrow_x, arrow_y - 4))      # Điểm trên
        polygon.append(QPointF(arrow_x + 6, arrow_y - 4))  # Điểm trên phải
        polygon.append(QPointF(arrow_x + 3, arrow_y + 3))  # Điểm dưới
        
        painter.drawPolygon(polygon)

class ModernRSAUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RSA - Encrypt & Decrypt")
        self.setGeometry(100, 50, 1200, 700)
        
        # State
        self.private_key = None
        self.public_key = None
        self.private_key_pem = ""
        self.public_key_pem = ""
        self.input_mode = 'file'  # 'text' or 'file'
        self.file_path = ''
        self.file_content = ''

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
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
        header = QLabel("RSA - Encrypt & Decrypt")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #1f2937; margin-bottom: 5px; border: none;")
        card_layout.addWidget(header)

        # Content Grid
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        card_layout.addLayout(content_layout)

        # ================= LEFT PANEL =================
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        content_layout.addLayout(left_panel, 3)

        # 1. Key Size Selection
        size_layout = QVBoxLayout()
        size_layout.setSpacing(5)
        
        label_size = QLabel("Key Size:")
        label_size.setStyleSheet("font-weight: 600; color: #374151; border: none; background: transparent; font-size: 20px;")
        size_layout.addWidget(label_size)
        
        self.key_size_combo = CustomComboBox()  # Sử dụng CustomComboBox
        self.key_size_combo.addItems(["1024 bits", "2048 bits", "4096 bits"])
        self.key_size_combo.setCurrentIndex(1)
        self.key_size_combo.setFixedHeight(45)
        self.key_size_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 10px;
                background-color: white;
                color: #1f2937;
                font-size: 16px;
            }
            QComboBox::down-arrow {
                width: 0px;
                height: 0px;
                border: none;
                image: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox:focus {
                border: 2px solid #3b82f6;
                padding: 9px;
            }
        """)
        size_layout.addWidget(self.key_size_combo)
        
        left_panel.addLayout(size_layout)

        # 2. Key Generation Button
        self.btn_generate = self.create_simple_button("Generate New Keys", "#10b981", "#059669", height=45)  # Màu xanh lá như Playfair
        left_panel.addWidget(self.btn_generate)

        # 3. Key Import Buttons - Đặt trên 1 dòng
        import_layout = QVBoxLayout()
        import_layout.setSpacing(5)
        
        label_import = QLabel("Key Import:")
        label_import.setStyleSheet("font-weight: 600; color: #374151; border: none; background: transparent; font-size: 20px;")
        import_layout.addWidget(label_import)
        
        # Tạo layout ngang cho 2 nút import
        import_buttons_layout = QHBoxLayout()
        import_buttons_layout.setSpacing(8)
        
        self.btn_import_public = self.create_simple_button("Import Public", "#3b82f6", "#2563eb", height=38)
        self.btn_import_private = self.create_simple_button("Import Private", "#3b82f6", "#2563eb", height=38)
        
        import_buttons_layout.addWidget(self.btn_import_public)
        import_buttons_layout.addWidget(self.btn_import_private)
        
        import_layout.addLayout(import_buttons_layout)
        left_panel.addLayout(import_layout)

        # 4. Key Display Area (Public & Private Keys) - Chiều cao cao hơn
        key_display_layout = QVBoxLayout()
        key_display_layout.setSpacing(5)
        
        label_keys = QLabel("Keys:")
        label_keys.setStyleSheet("font-weight: 600; color: #374151; border: none; background: transparent; font-size: 20px;")
        key_display_layout.addWidget(label_keys)
        
        # Public Key Display với chiều cao cao hơn
        public_key_label = QLabel("Public Key:")
        public_key_label.setStyleSheet("font-size: 16px; color: #374151; border: none; background: transparent; margin-top: 3px;")
        key_display_layout.addWidget(public_key_label)
        
        self.public_key_display = QTextEdit()
        self.public_key_display.setPlaceholderText("Public key will appear here...")
        self.public_key_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px;
                color: #1f2937;
                background-color: white;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                min-height: 90px;
                max-height: 90px;
            }
            QTextEdit:focus {
                border: 2px solid #3b82f6;
                padding: 7px;
            }
            QScrollBar:vertical { 
                border: none; 
                background: #f1f5f9; 
                width: 10px; 
                margin: 0px; 
                border-radius: 5px;
            }
            QScrollBar::handle:vertical { 
                background-color: #cbd5e1; 
                min-height: 15px; 
                border-radius: 5px; 
                margin: 1px; 
            }
            QScrollBar::handle:vertical:hover { 
                background-color: #94a3b8; 
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { 
                height: 0px; 
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { 
                background: none; 
            }
        """)
        self.public_key_display.setReadOnly(True)
        self.public_key_display.setLineWrapMode(QTextEdit.WidgetWidth)
        key_display_layout.addWidget(self.public_key_display)
        
        # Public Key Buttons - nhỏ hơn
        pub_btn_layout = QHBoxLayout()
        pub_btn_layout.setSpacing(6)
        self.btn_copy_public = self.create_simple_button("Copy", "#6b7280", "#4b5563", height=32)
        self.btn_save_public = self.create_simple_button("Save", "#6b7280", "#4b5563", height=32)
        pub_btn_layout.addWidget(self.btn_copy_public)
        pub_btn_layout.addWidget(self.btn_save_public)
        key_display_layout.addLayout(pub_btn_layout)
        
        # Spacer nhỏ giữa các key
        spacer1 = QLabel("")
        spacer1.setFixedHeight(5)
        key_display_layout.addWidget(spacer1)
        
        # Private Key Display với chiều cao cao hơn
        private_key_label = QLabel("Private Key:")
        private_key_label.setStyleSheet("font-size: 16px; color: #374151; border: none; background: transparent; margin-top: 3px;")
        key_display_layout.addWidget(private_key_label)
        
        self.private_key_display = QTextEdit()
        self.private_key_display.setPlaceholderText("Private key will appear here...")
        self.private_key_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px;
                color: #1f2937;
                background-color: white;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                min-height: 90px;
                max-height: 90px;
            }
            QTextEdit:focus {
                border: 2px solid #3b82f6;
                padding: 7px;
            }
            QScrollBar:vertical { 
                border: none; 
                background: #f1f5f9; 
                width: 10px; 
                margin: 0px; 
                border-radius: 5px;
            }
            QScrollBar::handle:vertical { 
                background-color: #cbd5e1; 
                min-height: 15px; 
                border-radius: 5px; 
                margin: 1px; 
            }
            QScrollBar::handle:vertical:hover { 
                background-color: #94a3b8; 
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { 
                height: 0px; 
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { 
                background: none; 
            }
        """)
        self.private_key_display.setReadOnly(True)
        self.private_key_display.setLineWrapMode(QTextEdit.WidgetWidth)
        key_display_layout.addWidget(self.private_key_display)
        
        # Private Key Buttons - nhỏ hơn
        priv_btn_layout = QHBoxLayout()
        priv_btn_layout.setSpacing(6)
        self.btn_copy_private = self.create_simple_button("Copy", "#6b7280", "#4b5563", height=32)
        self.btn_save_private = self.create_simple_button("Save", "#6b7280", "#4b5563", height=32)
        priv_btn_layout.addWidget(self.btn_copy_private)
        priv_btn_layout.addWidget(self.btn_save_private)
        key_display_layout.addLayout(priv_btn_layout)
        
        left_panel.addLayout(key_display_layout, 1)

        # Spacer nhỏ trước mode
        mode_spacer = QLabel("")
        mode_spacer.setFixedHeight(2)
        left_panel.addWidget(mode_spacer)

        # 5. Mode Selection
        mode_layout = QVBoxLayout()
        mode_layout.setSpacing(3)
        
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("font-weight: 600; color: #374151; border: none; background: transparent; font-size: 20px;")
        mode_layout.addWidget(mode_label)

        mode_radios = QHBoxLayout()
        mode_radios.setSpacing(25)
        self.radio_encrypt = QRadioButton("Encrypt")
        self.radio_decrypt = QRadioButton("Decrypt")
        self.radio_encrypt.setChecked(True)
        
        # Style cho radio buttons - giống Playfair UI
        radio_style = """
            QRadioButton { 
                color: #374151; 
                spacing: 10px; 
                font-size: 18px; 
                background-color: transparent;
                padding: 6px 0px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid #d1d5db;
                background-color: white;
            }
            QRadioButton::indicator:checked {
                background-color: #3b82f6;
                border: 2px solid #3b82f6;
            }
            QRadioButton::indicator:checked:hover {
                background-color: #2563eb;
                border: 2px solid #2563eb;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #94a3b8;
            }
        """
        self.radio_encrypt.setStyleSheet(radio_style)
        self.radio_decrypt.setStyleSheet(radio_style)

        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.radio_encrypt)
        self.mode_group.addButton(self.radio_decrypt)

        mode_radios.addWidget(self.radio_encrypt)
        mode_radios.addWidget(self.radio_decrypt)
        mode_radios.addStretch()
        mode_layout.addLayout(mode_radios)
        
        left_panel.addLayout(mode_layout)

        # Spacer trước buttons
        button_spacer = QLabel("")
        button_spacer.setFixedHeight(5)
        left_panel.addWidget(button_spacer)

        # 6. Action Buttons - Đặt trên 1 dòng
        button_layout = QHBoxLayout()  # Thay đổi từ QVBoxLayout sang QHBoxLayout
        button_layout.setSpacing(8)
        
        self.btn_execute = self.create_simple_button("▶ Execute", "#10b981", "#059669", height=45)  # Xanh lá như Playfair
        self.btn_clear = self.create_simple_button("🗑 Clear All", "#ef4444", "#dc2626", height=45)  # Đỏ như Playfair
        
        button_layout.addWidget(self.btn_execute)
        button_layout.addWidget(self.btn_clear)
        
        left_panel.addLayout(button_layout)
        left_panel.addStretch()

        # ================= RIGHT PANEL =================
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        content_layout.addLayout(right_panel, 7)

        # --- Input Tabs (File/Text) ---
        input_tab_layout = QVBoxLayout()
        input_tab_layout.setSpacing(5)

        # Tabs Header
        tab_header_layout = QHBoxLayout()
        tab_header_layout.setSpacing(15)
        
        self.btn_tab_file = QPushButton("File Input")
        self.btn_tab_text = QPushButton("Text Input")
        self.btn_tab_file.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_tab_text.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_tab_file.setFixedHeight(40)
        self.btn_tab_text.setFixedHeight(40)
        
        tab_header_layout.addWidget(self.btn_tab_file)
        tab_header_layout.addWidget(self.btn_tab_text)
        tab_header_layout.addStretch()
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #e5e7eb; background: transparent;")

        input_tab_layout.addLayout(tab_header_layout)
        input_tab_layout.addWidget(line)

        # Stacked widget for Input
        self.input_stack = QStackedWidget()
        self.input_stack.setStyleSheet("background-color: transparent;") 
        
        # --- File Input Page ---
        page_file = QWidget()
        page_file.setStyleSheet("background-color: transparent;")
        
        page_file_layout = QVBoxLayout(page_file)
        page_file_layout.setContentsMargins(0, 5, 0, 0)
        page_file_layout.setSpacing(8)

        lbl_path = QLabel("Path:")
        lbl_path.setStyleSheet("font-size: 20px; font-weight: 600; color: #374151; border: none; background: transparent;")
        page_file_layout.addWidget(lbl_path)

        # Row: Input + Button
        file_row_layout = QHBoxLayout()
        file_row_layout.setSpacing(8)

        self.inp_file_display = QLineEdit()
        self.inp_file_display.setReadOnly(True)
        self.inp_file_display.setPlaceholderText("Select input file...")
        self.inp_file_display.setStyleSheet("""
            QLineEdit {
                background-color: white; 
                border: 1px solid #d1d5db;
                border-radius: 6px; 
                padding: 10px; 
                color: #374151;
                font-size: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
                padding: 9px;
            }
        """)
        
        self.btn_browse = self.create_simple_button("Browse", "#a16207", "#854d0e", height=40)
        self.btn_browse.setFixedWidth(90)

        file_row_layout.addWidget(self.inp_file_display)
        file_row_layout.addWidget(self.btn_browse)
        
        page_file_layout.addLayout(file_row_layout)
        page_file_layout.addStretch(1)
        
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
        self.inp_text_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 10px;
                color: #1f2937;
                background-color: white;
                font-family: 'Segoe UI', sans-serif;
                font-size: 20px;
                min-height: 120px;
            }
            QTextEdit:focus {
                border: 2px solid #3b82f6;
                padding: 9px;
            }
            QScrollBar:vertical { 
                border: none; 
                background: #f1f5f9; 
                width: 12px; 
                margin: 0px; 
                border-radius: 6px;
            }
            QScrollBar::handle:vertical { 
                background-color: #cbd5e1; 
                min-height: 25px; 
                border-radius: 6px; 
                margin: 2px; 
            }
            QScrollBar::handle:vertical:hover { 
                background-color: #94a3b8; 
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { 
                height: 0px; 
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { 
                background: none; 
            }
        """)
        self.inp_text_area.setLineWrapMode(QTextEdit.WidgetWidth)
        page_text_layout.addWidget(self.inp_text_area, 1)
        page_text_layout.addStretch()

        self.input_stack.addWidget(page_file)
        self.input_stack.addWidget(page_text)
        input_tab_layout.addWidget(self.input_stack, 1)
        
        right_panel.addLayout(input_tab_layout)

        # --- Result Area ---
        result_layout = QVBoxLayout()
        result_layout.setSpacing(5)
        
        label_result = QLabel("Result:")
        label_result.setStyleSheet("font-size: 20px; font-weight: 600; color: #374151; border: none; background: transparent;")
        result_layout.addWidget(label_result)

        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("Result will appear here...")
        self.output_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 10px;
                color: #1f2937;
                background-color: white;
                font-family: 'Segoe UI', sans-serif;
                font-size: 20px;
                min-height: 120px;
            }
            QTextEdit:focus {
                border: 2px solid #3b82f6;
                padding: 9px;
            }
            QScrollBar:vertical { 
                border: none; 
                background: #f1f5f9; 
                width: 12px; 
                margin: 0px; 
                border-radius: 6px;
            }
            QScrollBar::handle:vertical { 
                background-color: #cbd5e1; 
                min-height: 25px; 
                border-radius: 6px; 
                margin: 2px; 
            }
            QScrollBar::handle:vertical:hover { 
                background-color: #94a3b8; 
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { 
                height: 0px; 
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { 
                background: none; 
            }
        """)
        self.output_text.setReadOnly(True)
        self.output_text.setLineWrapMode(QTextEdit.WidgetWidth)
        result_layout.addWidget(self.output_text, 1)
        
        right_panel.addLayout(result_layout, 1)

        # --- Action Buttons Right ---
        bottom_btns = QHBoxLayout()
        bottom_btns.setSpacing(8)
        
        self.btn_save_result = self.create_simple_button("💾 Save Result", "#2563eb", "#1d4ed8", height=42)
        self.btn_info = self.create_simple_button("💡 Learn Algorithm", "#efb013", "#d97706", height=42)
        self.btn_cancel = self.create_simple_button("← Cancel", "#6b7280", "#4b5563", height=42)
        
        bottom_btns.addWidget(self.btn_save_result)
        bottom_btns.addWidget(self.btn_info)
        bottom_btns.addWidget(self.btn_cancel)
        
        right_panel.addLayout(bottom_btns)

    # --- HELPER FUNCTIONS ---
    def create_simple_button(self, text, color, hover, height=40):
        btn = QPushButton(text)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(height)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}; 
                color: white; 
                font-weight: 600; 
                font-size: 15px;
                border-radius: 6px; 
                border: none;
                padding: 0px 12px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """)
        return btn

    def update_input_tab_style(self):
        active_style = """
            QPushButton {
                color: #2563eb; font-weight: bold; border: none;
                border-bottom: 2px solid #2563eb; background-color: transparent;
                font-size: 20px; padding-bottom: 4px;
            }
        """
        inactive_style = """
            QPushButton {
                color: #4b5563; font-weight: normal; border: none;
                border-bottom: 2px solid transparent; background-color: transparent;
                font-size: 20px; padding-bottom: 4px;
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

    def switch_tab(self, mode):
        self.input_mode = mode
        self.update_input_tab_style()

    def browse_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '', "Text files (*.txt);;All files (*.*)")
        if fname:
            self.file_path = fname
            self.inp_file_display.setText(fname)
            try:
                with open(fname, 'r', encoding='utf-8') as f:
                    self.file_content = f.read()
                    # Hiển thị nội dung file trong text input area
                    self.inp_text_area.setText(self.file_content)
                    # Chuyển sang tab text để xem nội dung
                    self.switch_tab('text')
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not read file: {e}")

    def get_input_text(self):
        if self.input_mode == 'file':
            return self.file_content
        else:
            return self.inp_text_area.toPlainText()

    # --- SỰ KIỆN CHUỘT - KHÔNG FOCUS KHI NHẤP VÀO KHOẢNG TRỐNG ---
    def mousePressEvent(self, event):
        # Lấy widget đang focus
        focused_widget = QApplication.focusWidget()
        if focused_widget:
            # Kiểm tra nếu click không phải vào widget đó
            if not self.is_child_widget(focused_widget, event.pos()):
                focused_widget.clearFocus()
        super().mousePressEvent(event)

    def is_child_widget(self, widget, pos):
        # Kiểm tra xem điểm click có nằm trong widget không
        widget_global_pos = widget.mapToGlobal(widget.rect().topLeft())
        widget_rect = widget.rect()
        widget_rect.moveTopLeft(widget_global_pos)
        
        return widget_rect.contains(self.mapToGlobal(pos))

    # --- CONNECTIONS ---
    def setup_connections(self):
        self.btn_generate.clicked.connect(self.generate_keys)
        self.btn_import_public.clicked.connect(self.import_public_key)
        self.btn_import_private.clicked.connect(self.import_private_key)
        self.btn_execute.clicked.connect(self.execute_operation)
        self.btn_clear.clicked.connect(self.clear_all)
        self.btn_copy_public.clicked.connect(lambda: self.copy_to_clipboard(self.public_key_display))
        self.btn_copy_private.clicked.connect(lambda: self.copy_to_clipboard(self.private_key_display))
        self.btn_save_result.clicked.connect(self.save_result)
        self.btn_save_public.clicked.connect(lambda: self.save_key_file(self.public_key_display, "public_key.pem"))
        self.btn_save_private.clicked.connect(lambda: self.save_key_file(self.private_key_display, "private_key.pem"))
        self.btn_info.clicked.connect(self.show_info)
        self.btn_cancel.clicked.connect(self.close)
        
        self.btn_tab_file.clicked.connect(lambda: self.switch_tab('file'))
        self.btn_tab_text.clicked.connect(lambda: self.switch_tab('text'))
        self.btn_browse.clicked.connect(self.browse_file)
        
        # Mặc định chọn tab Text Input
        self.switch_tab('file')

    # --- CORE RSA FUNCTIONS ---
    def generate_keys(self):
        try:
            key_size = int(self.key_size_combo.currentText().split()[0])
            
            # Generate private key
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            
            # Get public key
            self.public_key = self.private_key.public_key()
            
            # Serialize keys
            self.public_key_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
            
            self.private_key_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')
            
            # Display keys
            self.public_key_display.setText(self.public_key_pem)
            self.private_key_display.setText(self.private_key_pem)
            
            QMessageBox.information(self, "Success", f"Successfully generated {key_size}-bit RSA key pair!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate keys: {str(e)}")

    def import_public_key(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, 'Open Public Key', '', 
                "PEM files (*.pem);;All files (*.*)"
            )
            if filename:
                with open(filename, 'rb') as f:
                    key_data = f.read()
                
                self.public_key = serialization.load_pem_public_key(
                    key_data,
                    backend=default_backend()
                )
                
                self.public_key_pem = key_data.decode('utf-8')
                self.public_key_display.setText(self.public_key_pem)
                
                QMessageBox.information(self, "Success", "Public key imported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import public key: {str(e)}")

    def import_private_key(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, 'Open Private Key', '', 
                "PEM files (*.pem);;All files (*.*)"
            )
            if filename:
                with open(filename, 'rb') as f:
                    key_data = f.read()
                
                self.private_key = serialization.load_pem_private_key(
                    key_data,
                    password=None,
                    backend=default_backend()
                )
                
                self.private_key_pem = key_data.decode('utf-8')
                self.private_key_display.setText(self.private_key_pem)
                
                # Also extract public key from private key
                self.public_key = self.private_key.public_key()
                self.public_key_pem = self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8')
                self.public_key_display.setText(self.public_key_pem)
                
                QMessageBox.information(self, "Success", "Private key imported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import private key: {str(e)}")

    def execute_operation(self):
        mode = 'encrypt' if self.radio_encrypt.isChecked() else 'decrypt'
        
        if mode == 'encrypt':
            self.encrypt_text()
        else:
            self.decrypt_text()

    def encrypt_text(self):
        if not self.public_key:
            QMessageBox.warning(self, "Warning", "Please generate or import a public key first!")
            return
        
        try:
            plaintext = self.get_input_text().strip()
            if not plaintext:
                QMessageBox.warning(self, "Warning", "Please enter text to encrypt!")
                return
            
            # Encrypt with PKCS#1 v1.5 padding
            ciphertext = self.public_key.encrypt(
                plaintext.encode('utf-8'),
                padding.PKCS1v15()
            )
            
            # Convert to base64
            encrypted_base64 = base64.b64encode(ciphertext).decode('utf-8')
            
            self.output_text.setText(encrypted_base64)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Encryption failed: {str(e)}")

    def decrypt_text(self):
        if not self.private_key:
            QMessageBox.warning(self, "Warning", "Please generate or import a private key first!")
            return
        
        try:
            ciphertext_base64 = self.get_input_text().strip()
            if not ciphertext_base64:
                QMessageBox.warning(self, "Warning", "Please enter base64 text to decrypt!")
                return
            
            # Decode base64
            ciphertext = base64.b64decode(ciphertext_base64)
            
            # Decrypt with PKCS#1 v1.5 padding
            plaintext = self.private_key.decrypt(
                ciphertext,
                padding.PKCS1v15()
            ).decode('utf-8')
            
            self.output_text.setText(plaintext)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Decryption failed: {str(e)}")

    def save_key_file(self, text_widget, default_name):
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, 'Save Key File', default_name,
                "PEM files (*.pem);;All files (*.*)"
            )
            if filename:
                with open(filename, 'w') as f:
                    f.write(text_widget.toPlainText())
                QMessageBox.information(self, "Success", "Key saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def save_result(self):
        try:
            content = self.output_text.toPlainText().strip()
            if not content:
                QMessageBox.warning(self, "Warning", "No result to save!")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self, 'Save Result', 'result.txt',
                "Text files (*.txt);;All files (*.*)"
            )
            if filename:
                with open(filename, 'w') as f:
                    f.write(content)
                QMessageBox.information(self, "Success", "Result saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def copy_to_clipboard(self, text_widget):
        text = text_widget.toPlainText().strip()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(self, "Success", "Copied to clipboard!")
        else:
            QMessageBox.warning(self, "Warning", "No content to copy!")

    def clear_all(self):
        self.public_key = None
        self.private_key = None
        self.public_key_pem = ""
        self.private_key_pem = ""
        self.public_key_display.clear()
        self.private_key_display.clear()
        self.inp_text_area.clear()
        self.inp_file_display.clear()
        self.file_content = ''
        self.file_path = ''
        self.output_text.clear()
        QMessageBox.information(self, "Cleared", "All inputs and outputs have been cleared!")

    def show_info(self):
        info_text = """RSA (Rivest–Shamir–Adleman) is a public-key cryptosystem.

Key Features:
• Asymmetric encryption (public/private keys)
• Secure data transmission
• Digital signatures
• Key exchange protocol

How it works:
1. Generate key pair (public/private)
2. Encrypt with public key
3. Decrypt with private key
4. Keys are mathematically linked but one cannot be derived from the other

Security: Based on the practical difficulty of factoring large prime numbers."""
        
        QMessageBox.information(self, "RSA Algorithm Info", info_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 11)
    app.setFont(font)
    window = ModernRSAUI()
    window.show()
    sys.exit(app.exec_())