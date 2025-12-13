import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sys
import threading

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import algorithms (Giữ nguyên import của bạn)
try:
    from algorithms.caesar.caesar_cipher import crack_from_file as crack_caesar_file
    from algorithms.monoalphabetic.mono_cipher import crack_from_file as crack_mono_file
    from algorithms.vigenere.vigenere_cipher import crack_from_file as crack_vigenere_file
    from algorithms.des import DESModes
    from algorithms.aes import AESModes
    from utils.file_handler import (
        read_text_file, write_text_file,
        hex_to_bytes, bytes_to_hex,
        read_des_key_from_hex, read_des_iv_from_hex,
        save_encrypted_output, parse_encrypted_input
    )
except ImportError:
    # Đoạn này để tránh lỗi nếu chạy test mà không có folder algorithms
    # Bạn có thể xóa đoạn try-except này đi khi chạy thực tế
    pass

# --- CẤU HÌNH MÀU SẮC (THEME NÂU) ---
BROWN_COLOR = "#5D4037"       # Màu nâu đất
BROWN_HOVER = "#3E2723"       # Màu nâu đậm hơn khi di chuột
BUTTON_FONT = ("Roboto", 14, "bold")
TITLE_FONT = ("Roboto", 24, "bold")

GREEN_COLOR = "#4CAF50"   # Xanh lá chuẩn Material Design (green-500)
GREEN_HOVER = "#388E3C"   # Xanh lá đậm hơn khi hover (green-700)
RED_COLOR = "#D32F2F"       # Đỏ chính
RED_HOVER = "#B71C1C"       # Đỏ đậm khi hover
GRAY_COLOR = "#616161"      # Xám chính
GRAY_HOVER = "#424242"      # Xám đậm khi hover

ICON_CLEAR_TEXT = "🗑️ "   # Thùng rác
ICON_BACK_TEXT = "← "     # Mũi tên trái
ICON_RUN_TEXT = "▶ "      # Tam giác play (cho nút chính)

class CryptoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Cấu hình cửa sổ chính
        self.title("Đoàn Thanh Đệ - 23520282")
        self.geometry("1100x750")  # Tăng kích thước một chút cho thoáng
        
        # Thiết lập theme nền
        ctk.set_appearance_mode("light")  # Chế độ sáng để nền sáng hơn
        
        # Khởi tạo DES & AES
        try:
            self.des = DESModes()
            self.aes = AESModes()
        except:
            pass
        
        # Tạo content frame để chứa các màn hình
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Tạo main menu frame
        self.main_menu_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.setup_main_menu()
        self.main_menu_frame.pack(fill="both", expand=True)
        
        # Tạo các frame cho từng thuật toán (ẩn ban đầu)
        self.caesar_frame = ctk.CTkFrame(self.content_frame)
        self.setup_caesar_frame()
        
        self.mono_frame = ctk.CTkFrame(self.content_frame)
        self.setup_mono_frame()
        
        self.vigenere_frame = ctk.CTkFrame(self.content_frame)
        self.setup_vigenere_frame()
        
        self.des_frame = ctk.CTkFrame(self.content_frame)
        self.setup_des_frame()
        
        self.aes_frame = ctk.CTkFrame(self.content_frame)
        self.setup_aes_frame()
    
    def get_brown_button(self, master, text, command, width=200, height=50):
        """Helper để tạo nút màu nâu thống nhất"""
        return ctk.CTkButton(master, text=text, command=command,
                             width=width, height=height,
                             fg_color=BROWN_COLOR, hover_color=BROWN_HOVER,
                             font=BUTTON_FONT)
    
    def get_main_button(self, master, text, command, width=200, height=50):
        """Nút chính (Decrypt/Run) - màu nâu"""
        return ctk.CTkButton(master, text=text, command=command,
                            width=width, height=height,
                            fg_color=GREEN_COLOR, hover_color=GREEN_HOVER,
                            font=BUTTON_FONT)

    def get_clear_button(self, master, text, command, width=200, height=50):
        """Nút Clear - màu đỏ + icon"""
        return ctk.CTkButton(master, text=ICON_CLEAR_TEXT + text, command=command,
                            width=width, height=height,
                            fg_color=RED_COLOR, hover_color=RED_HOVER,
                            font=BUTTON_FONT)

    def get_back_button(self, master, text, command, width=200, height=50):
        """Nút Back - màu xám + icon"""
        return ctk.CTkButton(master, text=ICON_BACK_TEXT + text, command=command,
                            width=width, height=height,
                            fg_color=GRAY_COLOR, hover_color=GRAY_HOVER,
                            font=BUTTON_FONT)

    def setup_main_menu(self):
        """Giao diện menu chọn thuật toán (Đã chỉnh sửa layout)"""
        # Cấu hình lưới: 2 cột
        self.main_menu_frame.grid_columnconfigure((0, 1), weight=1)
        # Các dòng co giãn
        for i in range(5):
            self.main_menu_frame.grid_rowconfigure(i, weight=1)
        
        # Tiêu đề "CHOOSE ALGORITHM"
        title = ctk.CTkLabel(self.main_menu_frame, text="CHOOSE ALGORITHM",
                             font=TITLE_FONT, text_color=BROWN_COLOR)
        title.grid(row=0, column=0, columnspan=2, pady=(40, 20), sticky="ew")
        
        # Kích thước nút chung
        BTN_W = 350
        BTN_H = 80
        
        # Hàng 1: Caesar (Trái) - Vigenère (Phải)
        self.get_brown_button(self.main_menu_frame, "Caesar Cipher", self.show_caesar, BTN_W, BTN_H)\
            .grid(row=1, column=0, padx=20, pady=20)
            
        self.get_brown_button(self.main_menu_frame, "Vigenère Cipher", self.show_vigenere, BTN_W, BTN_H)\
            .grid(row=1, column=1, padx=20, pady=20)
            
        # Hàng 2: Mono-alphabetic (Giữa)
        self.get_brown_button(self.main_menu_frame, "Mono-alphabetic Substitution", self.show_mono, BTN_W, BTN_H)\
            .grid(row=2, column=0, columnspan=2, padx=20, pady=20)
            
        # Hàng 3: DES (Trái) - AES (Phải)
        self.get_brown_button(self.main_menu_frame, "DES Algorithm", self.show_des, BTN_W, BTN_H)\
            .grid(row=3, column=0, padx=20, pady=20)
            
        self.get_brown_button(self.main_menu_frame, "AES Algorithm", self.show_aes, BTN_W, BTN_H)\
            .grid(row=3, column=1, padx=20, pady=20)
    
    def hide_all_frames(self):
        """Ẩn tất cả các frame"""
        for frame in [self.main_menu_frame, self.caesar_frame, self.mono_frame,
                      self.vigenere_frame, self.des_frame, self.aes_frame]:
            frame.pack_forget()
    
    def show_caesar(self):
        self.hide_all_frames()
        self.caesar_frame.pack(fill="both", expand=True)
    
    def show_mono(self):
        self.hide_all_frames()
        self.mono_frame.pack(fill="both", expand=True)
    
    def show_vigenere(self):
        self.hide_all_frames()
        self.vigenere_frame.pack(fill="both", expand=True)
    
    def show_des(self):
        self.hide_all_frames()
        self.des_frame.pack(fill="both", expand=True)
    
    def show_aes(self):
        self.hide_all_frames()
        self.aes_frame.pack(fill="both", expand=True)
    
    def show_main_menu(self):
        self.hide_all_frames()
        self.main_menu_frame.pack(fill="both", expand=True)
    
    # ==================== CAESAR FRAME ====================

    def setup_caesar_frame(self):
        main_frame = self.caesar_frame
        # Tỷ lệ: Cột 0 (Controls) = 1, Cột 1 (Result) = 3 -> Result rộng hơn
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Tiêu đề
        title = ctk.CTkLabel(main_frame, text="Caesar Cipher - Brute Force Attack",
                             font=("Roboto", 20, "bold"), text_color=BROWN_COLOR)
        title.grid(row=0, column=0, columnspan=2, pady=(15, 10), sticky="ew")
        
        # --- LEFT FRAME (CONTROLS) ---
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Controls Inputs
        ctk.CTkLabel(left_frame, text="Ciphertext File:").pack(anchor="w", padx=10, pady=(10,0))
        input_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=5)
        self.caesar_input_entry = ctk.CTkEntry(input_frame)
        self.caesar_input_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(input_frame, text="Browse", width=60, height=28, fg_color=BROWN_COLOR, hover_color=BROWN_HOVER,
                      command=lambda: self.browse_file(self.caesar_input_entry)).pack(side="left", padx=(5,0))
        
        ctk.CTkLabel(left_frame, text="Output File:").pack(anchor="w", padx=10, pady=(10,0))
        output_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        output_frame.pack(fill="x", padx=10, pady=5)
        self.caesar_output_entry = ctk.CTkEntry(output_frame)
        self.caesar_output_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(output_frame, text="Browse", width=60, height=28, fg_color=BROWN_COLOR, hover_color=BROWN_HOVER,
                      command=lambda: self.save_file(self.caesar_output_entry)).pack(side="left", padx=(5,0))
        
        # Buttons (Xếp chồng dọc)
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=30)
        
        self.caesar_crack_btn = self.get_main_button(btn_frame, ICON_RUN_TEXT + "Decrypt Caesar", self.crack_caesar, width=200)
        self.caesar_crack_btn.pack(side="top", fill="x", pady=5)
       
        self.get_clear_button(btn_frame, "Clear", self.clear_caesar, width=200).pack(side="top", fill="x", pady=5)
        self.get_back_button(btn_frame, "Back to Menu", self.show_main_menu, width=200).pack(side="top", fill="x", pady=5)
        
        # --- RIGHT FRAME (RESULT) ---
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(right_frame, text="Result Preview:", font=("Roboto", 14, "bold")).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.caesar_result_text = ctk.CTkTextbox(right_frame, font=("Courier New", 14))
        self.caesar_result_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # ==================== MONO FRAME ====================

    def setup_mono_frame(self):
        main_frame = self.mono_frame
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3) # Result rộng hơn
        main_frame.grid_rowconfigure(1, weight=1)
        
        title = ctk.CTkLabel(main_frame, text="Mono-alphabetic Substitution - Frequency Analysis",
                             font=("Roboto", 20, "bold"), text_color=BROWN_COLOR)
        title.grid(row=0, column=0, columnspan=2, pady=(15, 10), sticky="ew")
        
        # Left Frame
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_columnconfigure(0, weight=1)

        # Inputs
        ctk.CTkLabel(left_frame, text="Ciphertext File:").pack(anchor="w", padx=10, pady=(10,0))
        input_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=5)
        self.mono_input_entry = ctk.CTkEntry(input_frame)
        self.mono_input_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(input_frame, text="Browse", width=60, height=28, fg_color=BROWN_COLOR, hover_color=BROWN_HOVER,
                      command=lambda: self.browse_file(self.mono_input_entry)).pack(side="left", padx=(5,0))
        
        ctk.CTkLabel(left_frame, text="Output File:").pack(anchor="w", padx=10, pady=(10,0))
        output_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        output_frame.pack(fill="x", padx=10, pady=5)
        self.mono_output_entry = ctk.CTkEntry(output_frame)
        self.mono_output_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(output_frame, text="Browse", width=60, height=28, fg_color=BROWN_COLOR, hover_color=BROWN_HOVER,
                      command=lambda: self.save_file(self.mono_output_entry)).pack(side="left", padx=(5,0))
        
        # Buttons (Stacked)
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=30)
        
        self.mono_crack_btn = self.get_main_button(btn_frame, ICON_RUN_TEXT + "Decrypt Mono-alphabetic", self.crack_mono, width=200)
        self.mono_crack_btn.pack(side="top", fill="x", pady=5)
       
        self.get_clear_button(btn_frame, "Clear", self.clear_mono, width=200).pack(side="top", fill="x", pady=5)
        self.get_back_button(btn_frame, "Back to Menu", self.show_main_menu, width=200).pack(side="top", fill="x", pady=5)
        
        # Right Frame
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(right_frame, text="Result Preview:", font=("Roboto", 14, "bold")).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.mono_result_text = ctk.CTkTextbox(right_frame, font=("Courier New", 14))
        self.mono_result_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # ==================== VIGENERE FRAME ====================

    def setup_vigenere_frame(self):
        main_frame = self.vigenere_frame
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3) # Result rộng hơn
        main_frame.grid_rowconfigure(1, weight=1)
        
        title = ctk.CTkLabel(main_frame, text="Vigenère Cipher - Kasiski & IC Analysis",
                             font=("Roboto", 20, "bold"), text_color=BROWN_COLOR)
        title.grid(row=0, column=0, columnspan=2, pady=(15, 10), sticky="ew")
        
        # Left Frame
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Inputs
        ctk.CTkLabel(left_frame, text="Ciphertext File:").pack(anchor="w", padx=10, pady=(10,0))
        input_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=5)
        self.vigenere_input_entry = ctk.CTkEntry(input_frame)
        self.vigenere_input_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(input_frame, text="Browse", width=60, height=28, fg_color=BROWN_COLOR, hover_color=BROWN_HOVER,
                      command=lambda: self.browse_file(self.vigenere_input_entry)).pack(side="left", padx=(5,0))
        
        ctk.CTkLabel(left_frame, text="Output File:").pack(anchor="w", padx=10, pady=(10,0))
        output_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        output_frame.pack(fill="x", padx=10, pady=5)
        self.vigenere_output_entry = ctk.CTkEntry(output_frame)
        self.vigenere_output_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(output_frame, text="Browse", width=60, height=28, fg_color=BROWN_COLOR, hover_color=BROWN_HOVER,
                      command=lambda: self.save_file(self.vigenere_output_entry)).pack(side="left", padx=(5,0))
        
        # Buttons (Stacked)
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=30)
        
        self.vigenere_crack_btn = self.get_main_button(btn_frame, ICON_RUN_TEXT + "Decrypt Vigenère", self.crack_vigenere, width=200)
        self.vigenere_crack_btn.pack(side="top", fill="x", pady=5)

        self.get_clear_button(btn_frame, "Clear", self.clear_vigenere, width=200).pack(side="top", fill="x", pady=5)
        self.get_back_button(btn_frame, "Back to Menu", self.show_main_menu, width=200).pack(side="top", fill="x", pady=5)
        
        # Right Frame
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(right_frame, text="Result Preview:", font=("Roboto", 14, "bold")).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.vigenere_result_text = ctk.CTkTextbox(right_frame, font=("Courier New", 14))
        self.vigenere_result_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # ==================== DES FRAME ====================

    def setup_des_frame(self):
        main_frame = self.des_frame
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3) # Result rộng hơn
        main_frame.grid_rowconfigure(1, weight=1)
        
        title = ctk.CTkLabel(main_frame, text="DES Encryption/Decryption",
                             font=("Roboto", 20, "bold"), text_color=BROWN_COLOR)
        title.grid(row=0, column=0, columnspan=2, pady=(15, 10), sticky="ew")
        
        # Left Frame
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Controls with grid layout for better alignment
        controls_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=10, pady=10)
        controls_frame.grid_columnconfigure(1, weight=1)

        # Mode
        ctk.CTkLabel(controls_frame, text="Mode:", anchor="w").grid(row=0, column=0, sticky="w", pady=5)
        mode_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        mode_frame.grid(row=0, column=1, sticky="ew", pady=5)
        self.des_mode_var = ctk.StringVar(value="ECB")
        ctk.CTkRadioButton(mode_frame, text="ECB", variable=self.des_mode_var, value="ECB", fg_color=BROWN_COLOR, command=self.on_des_mode_change).pack(side="left", padx=5)
        ctk.CTkRadioButton(mode_frame, text="CBC", variable=self.des_mode_var, value="CBC", fg_color=BROWN_COLOR, command=self.on_des_mode_change).pack(side="left", padx=5)
        
        # Action
        ctk.CTkLabel(controls_frame, text="Action:", anchor="w").grid(row=1, column=0, sticky="w", pady=5)
        action_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        action_frame.grid(row=1, column=1, sticky="ew", pady=5)
        self.des_action_var = ctk.StringVar(value="encrypt")
        ctk.CTkRadioButton(action_frame, text="Encrypt", variable=self.des_action_var, value="encrypt", fg_color=BROWN_COLOR).pack(side="left", padx=5)
        ctk.CTkRadioButton(action_frame, text="Decrypt", variable=self.des_action_var, value="decrypt", fg_color=BROWN_COLOR).pack(side="left", padx=5)
        
        # Key
        ctk.CTkLabel(controls_frame, text="Key (Hex):", anchor="w").grid(row=2, column=0, sticky="w", pady=5)
        self.des_key_entry = ctk.CTkEntry(controls_frame)
        self.des_key_entry.grid(row=2, column=1, sticky="ew", pady=5)
        ctk.CTkButton(controls_frame, text="Gen", width=40, fg_color=BROWN_COLOR, hover_color=BROWN_HOVER, command=self.generate_des_key).grid(row=2, column=2, padx=5)
        
        # IV
        ctk.CTkLabel(controls_frame, text="IV (Hex):", anchor="w").grid(row=3, column=0, sticky="w", pady=5)
        self.des_iv_entry = ctk.CTkEntry(controls_frame)
        self.des_iv_entry.grid(row=3, column=1, sticky="ew", pady=5)
        self.des_iv_btn = ctk.CTkButton(controls_frame, text="Gen", width=40, fg_color=BROWN_COLOR, hover_color=BROWN_HOVER, command=self.generate_des_iv, state="disabled")
        self.des_iv_btn.grid(row=3, column=2, padx=5)
        
        # Input File
        ctk.CTkLabel(controls_frame, text="Input:", anchor="w").grid(row=4, column=0, sticky="w", pady=5)
        self.des_input_entry = ctk.CTkEntry(controls_frame)
        self.des_input_entry.grid(row=4, column=1, sticky="ew", pady=5)
        ctk.CTkButton(controls_frame, text="...", width=40, fg_color=BROWN_COLOR, hover_color=BROWN_HOVER, command=lambda: self.browse_file(self.des_input_entry)).grid(row=4, column=2, padx=5)
        
        # Output File
        ctk.CTkLabel(controls_frame, text="Output:", anchor="w").grid(row=5, column=0, sticky="w", pady=5)
        self.des_output_entry = ctk.CTkEntry(controls_frame)
        self.des_output_entry.grid(row=5, column=1, sticky="ew", pady=5)
        ctk.CTkButton(controls_frame, text="...", width=40, fg_color=BROWN_COLOR, hover_color=BROWN_HOVER, command=lambda: self.save_file(self.des_output_entry)).grid(row=5, column=2, padx=5)
        
        # Buttons (Stacked)
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        self.des_execute_btn = self.get_main_button(btn_frame, ICON_RUN_TEXT + "Run DES", self.execute_des, width=200)
        self.des_execute_btn.pack(side="top", fill="x", pady=5)

        self.get_clear_button(btn_frame, "Clear", self.clear_des, width=200).pack(side="top", fill="x", pady=5)
        self.get_back_button(btn_frame, "Back to Menu", self.show_main_menu, width=200).pack(side="top", fill="x", pady=5)
        
        # Right Frame
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(right_frame, text="Result Preview:", font=("Roboto", 14, "bold")).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.des_result_text = ctk.CTkTextbox(right_frame, font=("Courier New", 14))
        self.des_result_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # ==================== AES FRAME ====================

    def setup_aes_frame(self):
        main_frame = self.aes_frame
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3) # Result rộng hơn
        main_frame.grid_rowconfigure(1, weight=1)
        
        title = ctk.CTkLabel(main_frame, text="AES-128 Encryption/Decryption",
                             font=("Roboto", 20, "bold"), text_color=BROWN_COLOR)
        title.grid(row=0, column=0, columnspan=2, pady=(15, 10), sticky="ew")
        
        # Left Frame
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Controls
        controls_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=10, pady=10)
        controls_frame.grid_columnconfigure(1, weight=1)

        # Mode
        ctk.CTkLabel(controls_frame, text="Mode:", anchor="w").grid(row=0, column=0, sticky="w", pady=5)
        mode_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        mode_frame.grid(row=0, column=1, sticky="ew", pady=5)
        self.aes_mode_var = ctk.StringVar(value="ECB")
        ctk.CTkRadioButton(mode_frame, text="ECB", variable=self.aes_mode_var, value="ECB", fg_color=BROWN_COLOR, command=self.on_aes_mode_change).pack(side="left", padx=5)
        ctk.CTkRadioButton(mode_frame, text="CBC", variable=self.aes_mode_var, value="CBC", fg_color=BROWN_COLOR, command=self.on_aes_mode_change).pack(side="left", padx=5)
        
        # Action
        ctk.CTkLabel(controls_frame, text="Action:", anchor="w").grid(row=1, column=0, sticky="w", pady=5)
        action_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        action_frame.grid(row=1, column=1, sticky="ew", pady=5)
        self.aes_action_var = ctk.StringVar(value="encrypt")
        ctk.CTkRadioButton(action_frame, text="Encrypt", variable=self.aes_action_var, value="encrypt", fg_color=BROWN_COLOR).pack(side="left", padx=5)
        ctk.CTkRadioButton(action_frame, text="Decrypt", variable=self.aes_action_var, value="decrypt", fg_color=BROWN_COLOR).pack(side="left", padx=5)
        
        # Key
        ctk.CTkLabel(controls_frame, text="Key (Hex):", anchor="w").grid(row=2, column=0, sticky="w", pady=5)
        self.aes_key_entry = ctk.CTkEntry(controls_frame)
        self.aes_key_entry.grid(row=2, column=1, sticky="ew", pady=5)
        ctk.CTkButton(controls_frame, text="Gen", width=40, fg_color=BROWN_COLOR, hover_color=BROWN_HOVER, command=self.generate_aes_key).grid(row=2, column=2, padx=5)
        
        # IV
        ctk.CTkLabel(controls_frame, text="IV (Hex):", anchor="w").grid(row=3, column=0, sticky="w", pady=5)
        self.aes_iv_entry = ctk.CTkEntry(controls_frame)
        self.aes_iv_entry.grid(row=3, column=1, sticky="ew", pady=5)
        self.aes_iv_btn = ctk.CTkButton(controls_frame, text="Gen", width=40, fg_color=BROWN_COLOR, hover_color=BROWN_HOVER, command=self.generate_aes_iv, state="disabled")
        self.aes_iv_btn.grid(row=3, column=2, padx=5)
        
        # Input File
        ctk.CTkLabel(controls_frame, text="Input:", anchor="w").grid(row=4, column=0, sticky="w", pady=5)
        self.aes_input_entry = ctk.CTkEntry(controls_frame)
        self.aes_input_entry.grid(row=4, column=1, sticky="ew", pady=5)
        ctk.CTkButton(controls_frame, text="...", width=40, fg_color=BROWN_COLOR, hover_color=BROWN_HOVER, command=lambda: self.browse_file(self.aes_input_entry)).grid(row=4, column=2, padx=5)
        
        # Output File
        ctk.CTkLabel(controls_frame, text="Output:", anchor="w").grid(row=5, column=0, sticky="w", pady=5)
        self.aes_output_entry = ctk.CTkEntry(controls_frame)
        self.aes_output_entry.grid(row=5, column=1, sticky="ew", pady=5)
        ctk.CTkButton(controls_frame, text="...", width=40, fg_color=BROWN_COLOR, hover_color=BROWN_HOVER, command=lambda: self.save_file(self.aes_output_entry)).grid(row=5, column=2, padx=5)
        
        # Buttons (Stacked)
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        self.aes_execute_btn = self.get_main_button(btn_frame, ICON_RUN_TEXT + "Run AES", self.execute_aes, width=200)
        self.aes_execute_btn.pack(side="top", fill="x", pady=5)

        self.get_clear_button(btn_frame, "Clear", self.clear_aes, width=200).pack(side="top", fill="x", pady=5)
        self.get_back_button(btn_frame, "Back to Menu", self.show_main_menu, width=200).pack(side="top", fill="x", pady=5)
        
        # Right Frame
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(right_frame, text="Result Preview:", font=("Roboto", 14, "bold")).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.aes_result_text = ctk.CTkTextbox(right_frame, font=("Courier New", 14))
        self.aes_result_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # ==================== DES FUNCTIONS ====================

    def on_des_mode_change(self):
        mode = self.des_mode_var.get()
        if mode == "CBC":
            self.des_iv_entry.configure(state="normal")
            self.des_iv_btn.configure(state="normal")
        else:
            self.des_iv_entry.configure(state="disabled")
            self.des_iv_btn.configure(state="disabled")
    
    def generate_des_key(self):
        import secrets
        key = secrets.token_hex(8).upper()
        self.des_key_entry.delete(0, "end")
        self.des_key_entry.insert(0, key)
        messagebox.showinfo("Success", f"Generated Key:\n{key}")
    
    def generate_des_iv(self):
        import secrets
        iv = secrets.token_hex(8).upper()
        self.des_iv_entry.delete(0, "end")
        self.des_iv_entry.insert(0, iv)
        messagebox.showinfo("Success", f"Generated IV:\n{iv}")
    
    def execute_des(self):
        mode = self.des_mode_var.get()
        action = self.des_action_var.get()
        input_file = self.des_input_entry.get()
        output_file = self.des_output_entry.get()
        key_hex = self.des_key_entry.get().strip()
        iv_hex = self.des_iv_entry.get().strip()
        
        if not input_file or not output_file:
            messagebox.showerror("Error", "Please select input and output file!")
            return
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist!")
            return
        if not key_hex:
            messagebox.showerror("Error", "Please enter key!")
            return
            
        try:
            key = read_des_key_from_hex(key_hex)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid key: {str(e)}")
            return
            
        iv = None
        if mode == 'CBC':
            if not iv_hex and action == 'encrypt':
                messagebox.showerror("Error", "IV is required for CBC encryption!")
                return
            if iv_hex:
                try:
                    iv = read_des_iv_from_hex(iv_hex)
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid IV: {str(e)}")
                    return
        
        self.des_execute_btn.configure(state="disabled", text="Processing...")
        self.des_result_text.delete("1.0", "end")
        self.des_result_text.insert("1.0", f"Executing DES {action}...\n")
        
        def run_des():
            try:
                if action == 'encrypt':
                    self.des_encrypt_file(input_file, output_file, key, mode, iv)
                else:
                    self.des_decrypt_file(input_file, output_file, key, mode, iv)
                self.after(0, lambda: self.des_execute_btn.configure(state="normal", text="Run DES"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Execution failed:\n{str(e)}"))
                self.after(0, lambda: self.des_execute_btn.configure(state="normal", text="Run Execute DES"))
        
        thread = threading.Thread(target=run_des)
        thread.daemon = True
        thread.start()
    
    def des_encrypt_file(self, input_file, output_file, key, mode, iv):
        plaintext = read_text_file(input_file).encode('utf-8')
        ciphertext, iv_used = self.des.encrypt(plaintext, key, mode=mode, iv=iv)
        ciphertext_hex = bytes_to_hex(ciphertext)
        iv_hex = bytes_to_hex(iv_used) if iv_used else None
        save_encrypted_output(output_file, ciphertext_hex, iv_hex, mode)
        
        result = f"✓ Encryption Successful!\nMode: {mode}\nKey: {bytes_to_hex(key).upper()}\n"
        if iv_hex: result += f"IV: {iv_hex.upper()}\n"
        result += f"\nCiphertext preview:\n{ciphertext_hex.upper()[:200]}..."
        
        self.after(0, lambda: self.des_result_text.delete("1.0", "end"))
        self.after(0, lambda: self.des_result_text.insert("1.0", result))
        self.after(0, lambda: messagebox.showinfo("Success", "File encrypted successfully!"))

    def des_decrypt_file(self, input_file, output_file, key, mode, iv):
        data = parse_encrypted_input(input_file)
        ciphertext = hex_to_bytes(data['ciphertext'])
        if mode == 'CBC' and iv is None:
            if data['iv']: iv = hex_to_bytes(data['iv'])
            else: raise ValueError("IV not found/provided!")
            
        plaintext = self.des.decrypt(ciphertext, key, mode=mode, iv=iv)
        write_text_file(output_file, plaintext.decode('utf-8'))
        
        result = f"✓ Decryption Successful!\nMode: {mode}\n\nPlaintext preview:\n{plaintext.decode('utf-8')[:999]}..."
        
        self.after(0, lambda: self.des_result_text.delete("1.0", "end"))
        self.after(0, lambda: self.des_result_text.insert("1.0", result))
        self.after(0, lambda: messagebox.showinfo("Success", "File decrypted successfully!"))

    # ==================== AES FUNCTIONS ====================
    def on_aes_mode_change(self):
        mode = self.aes_mode_var.get()
        if mode == "CBC":
            self.aes_iv_entry.configure(state="normal")
            self.aes_iv_btn.configure(state="normal")
        else:
            self.aes_iv_entry.configure(state="disabled")
            self.aes_iv_btn.configure(state="disabled")
            
    def generate_aes_key(self):
        import secrets
        key = secrets.token_hex(16).upper()
        self.aes_key_entry.delete(0, "end")
        self.aes_key_entry.insert(0, key)
        messagebox.showinfo("Success", f"Generated Key:\n{key}")

    def generate_aes_iv(self):
        import secrets
        iv = secrets.token_hex(16).upper()
        self.aes_iv_entry.delete(0, "end")
        self.aes_iv_entry.insert(0, iv)
        messagebox.showinfo("Success", f"Generated IV:\n{iv}")

    def execute_aes(self):
        mode = self.aes_mode_var.get()
        action = self.aes_action_var.get()
        input_file = self.aes_input_entry.get()
        output_file = self.aes_output_entry.get()
        key_hex = self.aes_key_entry.get().strip()
        iv_hex = self.aes_iv_entry.get().strip()
        
        if not input_file or not output_file:
            messagebox.showerror("Error", "Please select files!")
            return
        if not key_hex:
            messagebox.showerror("Error", "Please enter key!")
            return
            
        try:
            key = hex_to_bytes(key_hex)
            if len(key) != 16: raise ValueError("Key must be 16 bytes")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid key: {str(e)}")
            return
            
        iv = None
        if mode == 'CBC':
            if not iv_hex and action == 'encrypt':
                messagebox.showerror("Error", "IV required for CBC!")
                return
            if iv_hex:
                try:
                    iv = hex_to_bytes(iv_hex)
                except:
                    messagebox.showerror("Error", "Invalid IV")
                    return

        self.aes_execute_btn.configure(state="disabled", text="Processing...")
        self.aes_result_text.delete("1.0", "end")
        self.aes_result_text.insert("1.0", f"Executing AES {action}...\n")
        
        def run_aes():
            try:
                if action == 'encrypt':
                    self.aes_encrypt_file(input_file, output_file, key, mode, iv)
                else:
                    self.aes_decrypt_file(input_file, output_file, key, mode, iv)
                self.after(0, lambda: self.aes_execute_btn.configure(state="normal", text="Run AES"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Execution failed:\n{str(e)}"))
                self.after(0, lambda: self.aes_execute_btn.configure(state="normal", text="Run AES"))
        
        thread = threading.Thread(target=run_aes)
        thread.daemon = True
        thread.start()

    def aes_encrypt_file(self, input_file, output_file, key, mode, iv):
        plaintext = read_text_file(input_file).encode('utf-8')
        ciphertext, iv_used = self.aes.encrypt(plaintext, key, mode=mode, iv=iv)
        ciphertext_hex = bytes_to_hex(ciphertext)
        iv_hex = bytes_to_hex(iv_used) if iv_used else None
        save_encrypted_output(output_file, ciphertext_hex, iv_hex, mode)
        
        result = f"✓ Encryption Successful!\nMode: {mode}\nKey: {bytes_to_hex(key).upper()}\n"
        result += f"\nCiphertext preview:\n{ciphertext_hex.upper()[:200]}..."
        
        self.after(0, lambda: self.aes_result_text.delete("1.0", "end"))
        self.after(0, lambda: self.aes_result_text.insert("1.0", result))
        self.after(0, lambda: messagebox.showinfo("Success", "File encrypted successfully!"))

    def aes_decrypt_file(self, input_file, output_file, key, mode, iv):
        data = parse_encrypted_input(input_file)
        ciphertext = hex_to_bytes(data['ciphertext'])
        if mode == 'CBC' and iv is None:
            if data['iv']: iv = hex_to_bytes(data['iv'])
            else: raise ValueError("IV missing!")
        
        plaintext = self.aes.decrypt(ciphertext, key, mode=mode, iv=iv)
        write_text_file(output_file, plaintext.decode('utf-8'))
        
        result = f"Decryption Successful!\nMode: {mode}\n\nPlaintext preview:\n{plaintext.decode('utf-8')[:999]}..."
        
        self.after(0, lambda: self.aes_result_text.delete("1.0", "end"))
        self.after(0, lambda: self.aes_result_text.insert("1.0", result))
        self.after(0, lambda: messagebox.showinfo("Success", "File decrypted successfully!"))

    # ==================== CAESAR FUNCTIONS ====================
    
    def crack_caesar(self):
        input_file = self.caesar_input_entry.get()
        output_file = self.caesar_output_entry.get()
        if not input_file or not output_file:
            messagebox.showerror("Error", "Select files!")
            return
        
        self.caesar_crack_btn.configure(state="disabled", text="...")
        
        def run():
            try:
                key, plaintext = crack_caesar_file(input_file, output_file)
                self.after(0, lambda: self.update_caesar_result(key, plaintext, output_file))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.after(0, lambda: self.caesar_crack_btn.configure(state="normal", text="Decrypt Caesar"))
        threading.Thread(target=run, daemon=True).start()

    def update_caesar_result(self, key, plaintext, output_file):
        self.caesar_result_text.delete("1.0", "end")
        res = f"Key: {key}\nPlaintext:\n{plaintext[:999]}..."
        self.caesar_result_text.insert("1.0", res)
        self.caesar_crack_btn.configure(state="normal", text="Decrypt Caesar")

    # ==================== MONOALPHABETIC FUNCTIONS ====================        

    def crack_mono(self):
        input_file = self.mono_input_entry.get()
        output_file = self.mono_output_entry.get()
        if not input_file or not output_file: return
        self.mono_crack_btn.configure(state="disabled", text="...")
        
        def run():
            try:
                mapping, plaintext, score = crack_mono_file(input_file, output_file)
                self.after(0, lambda: self.update_mono_result(mapping, plaintext, score, output_file))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.after(0, lambda: self.mono_crack_btn.configure(state="normal", text="Decrypt Mono-alphabetic"))
        threading.Thread(target=run, daemon=True).start()

    def update_mono_result(self, mapping, plaintext, score, output_file):
        self.mono_result_text.delete("1.0", "end")
        res = f"Score: {score:.4f}\nPlaintext:\n{plaintext[:999]}..."
        self.mono_result_text.insert("1.0", res)
        self.mono_crack_btn.configure(state="normal", text="Decrypt Mono-alphabetic")

    # ==================== VIGENERE FUNCTIONS ====================  

    def crack_vigenere(self):
        input_file = self.vigenere_input_entry.get()
        output_file = self.vigenere_output_entry.get()
        if not input_file or not output_file: return
        self.vigenere_crack_btn.configure(state="disabled", text="...")
        
        def run():
            try:
                key, plaintext = crack_vigenere_file(input_file, output_file)
                self.after(0, lambda: self.update_vigenere_result(key, plaintext, output_file))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.after(0, lambda: self.vigenere_crack_btn.configure(state="normal", text="Decrypt Vigenère"))
        threading.Thread(target=run, daemon=True).start()

    def update_vigenere_result(self, key, plaintext, output_file):
        self.vigenere_result_text.delete("1.0", "end")
        res = f"Key: {key}\nPlaintext:\n{plaintext[:999]}..."
        self.vigenere_result_text.insert("1.0", res)
        self.vigenere_crack_btn.configure(state="normal", text="Decrypt Vigenère")

    # ==================== COMMON FUNCTIONS ====================

    def browse_file(self, entry):
        filename = filedialog.askopenfilename(filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if filename:
            entry.delete(0, "end")
            entry.insert(0, filename)
    
    def save_file(self, entry):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if filename:
            entry.delete(0, "end")
            entry.insert(0, filename)
    
    def clear_caesar(self):
        self.caesar_input_entry.delete(0, "end")
        self.caesar_output_entry.delete(0, "end")
        self.caesar_result_text.delete("1.0", "end")
    def clear_mono(self):
        self.mono_input_entry.delete(0, "end")
        self.mono_output_entry.delete(0, "end")
        self.mono_result_text.delete("1.0", "end")
    def clear_vigenere(self):
        self.vigenere_input_entry.delete(0, "end")
        self.vigenere_output_entry.delete(0, "end")
        self.vigenere_result_text.delete("1.0", "end")
    def clear_des(self):
        self.des_input_entry.delete(0, "end")
        self.des_output_entry.delete(0, "end")
        self.des_key_entry.delete(0, "end")
        self.des_iv_entry.delete(0, "end")
        self.des_result_text.delete("1.0", "end")
    def clear_aes(self):
        self.aes_input_entry.delete(0, "end")
        self.aes_output_entry.delete(0, "end")
        self.aes_key_entry.delete(0, "end")
        self.aes_iv_entry.delete(0, "end")
        self.aes_result_text.delete("1.0", "end")

if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()