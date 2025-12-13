import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sys
import threading

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import algorithms
from algorithms.caesar.caesar_cipher import crack_from_file as crack_caesar_file
from algorithms.monoalphabetic.mono_cipher import crack_from_file as crack_mono_file
from algorithms.vigenere.vigenere_cipher import crack_from_file as crack_vigenere_file
from algorithms.des import DESModes
from algorithms.aes import AESModes  
from explanation_viewer import ExplanationViewer
from utils.file_handler import (
    read_text_file, write_text_file,
    hex_to_bytes, bytes_to_hex,
    read_des_key_from_hex, read_des_iv_from_hex,
    save_encrypted_output, parse_encrypted_input
)


class CryptoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Cấu hình cửa sổ chính
        self.title("Lab 06 - Review of Encryption Algorithms")
        self.geometry("1000x700")
        
        # Thiết lập theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Khởi tạo DES & AES
        self.des = DESModes()
        # self.aes = AESModes() # Có thể khởi tạo ở đây hoặc trong hàm xử lý tùy ý
        
        # Tạo tabview
        self.tabview = ctk.CTkTabview(self, width=950, height=650)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Thêm các tab
        self.tab_caesar = self.tabview.add("Caesar Cipher")
        self.tab_mono = self.tabview.add("Mono-alphabetic")
        self.tab_vigenere = self.tabview.add("Vigenère Cipher")
        self.tab_des = self.tabview.add("DES")
        self.tab_aes = self.tabview.add("AES")
        
        # Khởi tạo giao diện cho từng tab
        self.setup_caesar_tab()
        self.setup_mono_tab()
        self.setup_vigenere_tab()
        self.setup_des_tab()
        self.setup_aes_tab()
    
    # ==================== CAESAR TAB ====================
    def setup_caesar_tab(self):
        """Giao diện cho Caesar Cipher"""
        main_frame = ctk.CTkFrame(self.tab_caesar)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(main_frame, text="Caesar Cipher - Brute Force Attack", 
                            font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=15)
        
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(controls_frame, text="Ciphertext File:", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.caesar_input_entry = ctk.CTkEntry(controls_frame, width=500)
        self.caesar_input_entry.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(controls_frame, text="Browse", width=100,
                     command=lambda: self.browse_file(self.caesar_input_entry)).grid(row=0, column=2, padx=10, pady=10)
        
        ctk.CTkLabel(controls_frame, text="Output File:", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.caesar_output_entry = ctk.CTkEntry(controls_frame, width=500)
        self.caesar_output_entry.grid(row=1, column=1, padx=10, pady=10)
        ctk.CTkButton(controls_frame, text="Browse", width=100,
                     command=lambda: self.save_file(self.caesar_output_entry)).grid(row=1, column=2, padx=10, pady=10)
        
        result_label = ctk.CTkLabel(main_frame, text="Result Preview:", 
                                   font=ctk.CTkFont(size=14))
        result_label.pack(pady=(20, 5))
        
        self.caesar_result_text = ctk.CTkTextbox(main_frame, width=850, height=300)
        self.caesar_result_text.pack(padx=20, pady=5)
        
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(pady=20)
        
        self.caesar_crack_btn = ctk.CTkButton(btn_frame, text="🔓 Crack Caesar Cipher", width=200, height=40,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     command=self.crack_caesar)
        self.caesar_crack_btn.pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Clear", width=100, height=40,
                     command=self.clear_caesar).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="📖 Giải thích",
            width=150,
            height=40,
            fg_color="green",
            hover_color="darkgreen",
            command=lambda: ExplanationViewer(self, "Caesar Cipher")
        ).pack(side="left", padx=10)
    
    # ==================== MONO TAB ====================
    def setup_mono_tab(self):
        """Giao diện cho Mono-alphabetic Substitution"""
        main_frame = ctk.CTkFrame(self.tab_mono)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(main_frame, text="Mono-alphabetic Substitution - Frequency Analysis", 
                            font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=15)
        
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(controls_frame, text="Ciphertext File:", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.mono_input_entry = ctk.CTkEntry(controls_frame, width=500)
        self.mono_input_entry.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(controls_frame, text="Browse", width=100,
                     command=lambda: self.browse_file(self.mono_input_entry)).grid(row=0, column=2, padx=10, pady=10)
        
        ctk.CTkLabel(controls_frame, text="Output File:", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.mono_output_entry = ctk.CTkEntry(controls_frame, width=500)
        self.mono_output_entry.grid(row=1, column=1, padx=10, pady=10)
        ctk.CTkButton(controls_frame, text="Browse", width=100,
                     command=lambda: self.save_file(self.mono_output_entry)).grid(row=1, column=2, padx=10, pady=10)
        
        result_label = ctk.CTkLabel(main_frame, text="Result Preview:", 
                                   font=ctk.CTkFont(size=14))
        result_label.pack(pady=(20, 5))
        
        self.mono_result_text = ctk.CTkTextbox(main_frame, width=850, height=300)
        self.mono_result_text.pack(padx=20, pady=5)
        
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(pady=20)
        
        self.mono_crack_btn = ctk.CTkButton(btn_frame, text="🔍 Analyze & Decrypt", width=200, height=40,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     command=self.crack_mono)
        self.mono_crack_btn.pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Clear", width=100, height=40,
                     command=self.clear_mono).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="📖 Giải thích",
            width=150,
            height=40,
            fg_color="green",
            hover_color="darkgreen",
            command=lambda: ExplanationViewer(self, "Monoalphabetic Substitution")
        ).pack(side="left", padx=10)
    
    # ==================== VIGENERE TAB ====================
    def setup_vigenere_tab(self):
        """Giao diện cho Vigenère Cipher"""
        main_frame = ctk.CTkFrame(self.tab_vigenere)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(main_frame, text="Vigenère Cipher - Kasiski & IC Analysis", 
                            font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=15)
        
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(controls_frame, text="Ciphertext File:", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.vigenere_input_entry = ctk.CTkEntry(controls_frame, width=500)
        self.vigenere_input_entry.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(controls_frame, text="Browse", width=100,
                     command=lambda: self.browse_file(self.vigenere_input_entry)).grid(row=0, column=2, padx=10, pady=10)
        
        ctk.CTkLabel(controls_frame, text="Output File:", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.vigenere_output_entry = ctk.CTkEntry(controls_frame, width=500)
        self.vigenere_output_entry.grid(row=1, column=1, padx=10, pady=10)
        ctk.CTkButton(controls_frame, text="Browse", width=100,
                     command=lambda: self.save_file(self.vigenere_output_entry)).grid(row=1, column=2, padx=10, pady=10)
        
        result_label = ctk.CTkLabel(main_frame, text="Result Preview:", 
                                   font=ctk.CTkFont(size=14))
        result_label.pack(pady=(20, 5))
        
        self.vigenere_result_text = ctk.CTkTextbox(main_frame, width=850, height=300)
        self.vigenere_result_text.pack(padx=20, pady=5)
        
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(pady=20)
        
        self.vigenere_crack_btn = ctk.CTkButton(btn_frame, text="🔑 Crack Vigenère", width=200, height=40,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     command=self.crack_vigenere)
        self.vigenere_crack_btn.pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Clear", width=100, height=40,
                     command=self.clear_vigenere).pack(side="left", padx=10)
        

        ctk.CTkButton(
            btn_frame, 
            text="📖 Giải thích",
            width=150,
            height=40,
            fg_color="green",
            hover_color="darkgreen",
            command=lambda: ExplanationViewer(self, "Vigenère Cipher")
        ).pack(side="left", padx=10)
    
    # ==================== DES TAB ====================
    def setup_des_tab(self):
        """Giao diện cho DES - ĐÃ CẬP NHẬT"""
        main_frame = ctk.CTkFrame(self.tab_des)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(main_frame, text="DES Encryption/Decryption", 
                            font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=15)
        
        # Frame chứa các controls với grid
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=40, pady=10)
        
        # Mode selection row
        ctk.CTkLabel(controls_frame, text="Mode:", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(
                        row=0, column=0, padx=10, pady=10, sticky="w")
        mode_frame = ctk.CTkFrame(controls_frame)
        mode_frame.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        self.des_mode_var = ctk.StringVar(value="ECB")
        ctk.CTkRadioButton(mode_frame, text="ECB", variable=self.des_mode_var, 
                          value="ECB", command=self.on_des_mode_change).pack(side="left", padx=10)
        ctk.CTkRadioButton(mode_frame, text="CBC", variable=self.des_mode_var, 
                          value="CBC", command=self.on_des_mode_change).pack(side="left", padx=10)
        
        # Action selection row
        ctk.CTkLabel(controls_frame, text="Action:", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(
                        row=1, column=0, padx=10, pady=10, sticky="w")
        action_frame = ctk.CTkFrame(controls_frame)
        action_frame.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        self.des_action_var = ctk.StringVar(value="encrypt")
        ctk.CTkRadioButton(action_frame, text="Encrypt", variable=self.des_action_var, 
                          value="encrypt").pack(side="left", padx=10)
        ctk.CTkRadioButton(action_frame, text="Decrypt", variable=self.des_action_var, 
                          value="decrypt").pack(side="left", padx=10)
        
        # Key input row
        ctk.CTkLabel(controls_frame, text="Key (16 hex chars):", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(
                        row=2, column=0, padx=10, pady=10, sticky="w")
        self.des_key_entry = ctk.CTkEntry(controls_frame, width=350, 
                                         placeholder_text="e.g., 0123456789ABCDEF")
        self.des_key_entry.grid(row=2, column=1, padx=10, pady=10)
        ctk.CTkButton(controls_frame, text="Generate Random", width=150,
                     command=self.generate_des_key).grid(row=2, column=2, padx=10, pady=10)
        
        # IV input row
        ctk.CTkLabel(controls_frame, text="IV (16 hex chars):", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(
                        row=3, column=0, padx=10, pady=10, sticky="w")
        self.des_iv_entry = ctk.CTkEntry(controls_frame, width=350, 
                                        placeholder_text="Required for CBC mode")
        self.des_iv_entry.grid(row=3, column=1, padx=10, pady=10)
        self.des_iv_btn = ctk.CTkButton(controls_frame, text="Generate Random", width=150,
                     command=self.generate_des_iv, state="disabled")
        self.des_iv_btn.grid(row=3, column=2, padx=10, pady=10)
        
        # Input file row
        ctk.CTkLabel(controls_frame, text="Input File:", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(
                        row=4, column=0, padx=10, pady=10, sticky="w")
        self.des_input_entry = ctk.CTkEntry(controls_frame, width=350)
        self.des_input_entry.grid(row=4, column=1, padx=10, pady=10)
        ctk.CTkButton(controls_frame, text="Browse", width=150,
                     command=lambda: self.browse_file(self.des_input_entry)).grid(
                         row=4, column=2, padx=10, pady=10)
        
        # Output file row
        ctk.CTkLabel(controls_frame, text="Output File:", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(
                        row=5, column=0, padx=10, pady=10, sticky="w")
        self.des_output_entry = ctk.CTkEntry(controls_frame, width=350)
        self.des_output_entry.grid(row=5, column=1, padx=10, pady=10)
        ctk.CTkButton(controls_frame, text="Browse", width=150,
                     command=lambda: self.save_file(self.des_output_entry)).grid(
                         row=5, column=2, padx=10, pady=10)
        
        # Result area
        result_label = ctk.CTkLabel(main_frame, text="Result Preview:", 
                                   font=ctk.CTkFont(size=14))
        result_label.pack(pady=(10, 5))
        
        self.des_result_text = ctk.CTkTextbox(main_frame, width=850, height=150)
        self.des_result_text.pack(padx=20, pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(pady=15)
        
        self.des_execute_btn = ctk.CTkButton(btn_frame, text="🔐 Execute DES", width=200, height=40,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     command=self.execute_des)
        self.des_execute_btn.pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Clear", width=100, height=40,
                     command=self.clear_des).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="📖 Giải thích",
            width=150,
            height=40,
            fg_color="green",
            hover_color="darkgreen",
            command=lambda: ExplanationViewer(self, "DES")
        ).pack(side="left", padx=10)
    
    # ==================== AES TAB ====================
    def setup_aes_tab(self):
        """Giao diện cho AES - ĐÃ HOÀN THIỆN"""
        main_frame = ctk.CTkFrame(self.tab_aes)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(main_frame, text="AES-128 Encryption/Decryption", 
                            font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=15)
        
        # Frame chứa các controls với grid
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=40, pady=10)
        
        # Mode selection row
        ctk.CTkLabel(controls_frame, text="Mode:", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(
                        row=0, column=0, padx=10, pady=10, sticky="w")
        mode_frame = ctk.CTkFrame(controls_frame)
        mode_frame.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        self.aes_mode_var = ctk.StringVar(value="ECB")
        ctk.CTkRadioButton(mode_frame, text="ECB", variable=self.aes_mode_var, 
                          value="ECB", command=self.on_aes_mode_change).pack(side="left", padx=10)
        ctk.CTkRadioButton(mode_frame, text="CBC", variable=self.aes_mode_var, 
                          value="CBC", command=self.on_aes_mode_change).pack(side="left", padx=10)
        
        # Action selection row
        ctk.CTkLabel(controls_frame, text="Action:", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(
                        row=1, column=0, padx=10, pady=10, sticky="w")
        action_frame = ctk.CTkFrame(controls_frame)
        action_frame.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        self.aes_action_var = ctk.StringVar(value="encrypt")
        ctk.CTkRadioButton(action_frame, text="Encrypt", variable=self.aes_action_var, 
                          value="encrypt").pack(side="left", padx=10)
        ctk.CTkRadioButton(action_frame, text="Decrypt", variable=self.aes_action_var, 
                          value="decrypt").pack(side="left", padx=10)
        
        # Key input row
        ctk.CTkLabel(controls_frame, text="Key (32 hex chars):", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(
                        row=2, column=0, padx=10, pady=10, sticky="w")
        self.aes_key_entry = ctk.CTkEntry(controls_frame, width=350, 
                                         placeholder_text="e.g., 0123456789ABCDEF0123456789ABCDEF")
        self.aes_key_entry.grid(row=2, column=1, padx=10, pady=10)
        ctk.CTkButton(controls_frame, text="Generate Random", width=150,
                     command=self.generate_aes_key).grid(row=2, column=2, padx=10, pady=10)
        
        # IV input row
        ctk.CTkLabel(controls_frame, text="IV (32 hex chars):", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(
                        row=3, column=0, padx=10, pady=10, sticky="w")
        self.aes_iv_entry = ctk.CTkEntry(controls_frame, width=350, 
                                        placeholder_text="Required for CBC mode")
        self.aes_iv_entry.grid(row=3, column=1, padx=10, pady=10)
        self.aes_iv_btn = ctk.CTkButton(controls_frame, text="Generate Random", width=150,
                     command=self.generate_aes_iv, state="disabled")
        self.aes_iv_btn.grid(row=3, column=2, padx=10, pady=10)
        
        # Input file row
        ctk.CTkLabel(controls_frame, text="Input File:", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(
                        row=4, column=0, padx=10, pady=10, sticky="w")
        self.aes_input_entry = ctk.CTkEntry(controls_frame, width=350)
        self.aes_input_entry.grid(row=4, column=1, padx=10, pady=10)
        ctk.CTkButton(controls_frame, text="Browse", width=150,
                     command=lambda: self.browse_file(self.aes_input_entry)).grid(
                         row=4, column=2, padx=10, pady=10)
        
        # Output file row
        ctk.CTkLabel(controls_frame, text="Output File:", 
                    font=ctk.CTkFont(size=14), width=140, anchor="w").grid(
                        row=5, column=0, padx=10, pady=10, sticky="w")
        self.aes_output_entry = ctk.CTkEntry(controls_frame, width=350)
        self.aes_output_entry.grid(row=5, column=1, padx=10, pady=10)
        ctk.CTkButton(controls_frame, text="Browse", width=150,
                     command=lambda: self.save_file(self.aes_output_entry)).grid(
                         row=5, column=2, padx=10, pady=10)
        
        # Result area
        result_label = ctk.CTkLabel(main_frame, text="Result Preview:", 
                                   font=ctk.CTkFont(size=14))
        result_label.pack(pady=(10, 5))
        
        self.aes_result_text = ctk.CTkTextbox(main_frame, width=850, height=150)
        self.aes_result_text.pack(padx=20, pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(pady=15)
        
        self.aes_execute_btn = ctk.CTkButton(btn_frame, text="🔐 Execute AES", width=200, height=40,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     command=self.execute_aes)
        self.aes_execute_btn.pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Clear", width=100, height=40,
                     command=self.clear_aes).pack(side="left", padx=10)
        

        ctk.CTkButton(
            btn_frame, 
            text="📖 Giải thích",
            width=150,
            height=40,
            fg_color="green",
            hover_color="darkgreen",
            command=lambda: ExplanationViewer(self, "AES")
        ).pack(side="left", padx=10)
    
    # ==================== DES FUNCTIONS ====================
    
    def on_des_mode_change(self):
        """Enable/disable IV field based on mode"""
        mode = self.des_mode_var.get()
        if mode == "CBC":
            self.des_iv_entry.configure(state="normal")
            self.des_iv_btn.configure(state="normal")
        else:
            self.des_iv_entry.configure(state="normal")
            self.des_iv_btn.configure(state="disabled")
    
    def generate_des_key(self):
        """Generate random DES key"""
        import secrets
        key = secrets.token_hex(8)  # 8 bytes = 16 hex chars
        self.des_key_entry.delete(0, "end")
        self.des_key_entry.insert(0, key.upper())
        messagebox.showinfo("Success", f"Generated Key:\n{key.upper()}")
    
    def generate_des_iv(self):
        """Generate random DES IV"""
        import secrets
        iv = secrets.token_hex(8)  # 8 bytes = 16 hex chars
        self.des_iv_entry.delete(0, "end")
        self.des_iv_entry.insert(0, iv.upper())
        messagebox.showinfo("Success", f"Generated IV:\n{iv.upper()}")
    
    def execute_des(self):
        """Execute DES encryption/decryption"""
        # Validate inputs
        mode = self.des_mode_var.get()
        action = self.des_action_var.get()
        input_file = self.des_input_entry.get()
        output_file = self.des_output_entry.get()
        key_hex = self.des_key_entry.get().strip()
        iv_hex = self.des_iv_entry.get().strip()
        
        if not input_file:
            messagebox.showerror("Error", "Please select input file!")
            return
        
        if not output_file:
            messagebox.showerror("Error", "Please select output file!")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist!")
            return
        
        if not key_hex:
            messagebox.showerror("Error", "Please enter key!")
            return
        
        # Validate key
        try:
            key = read_des_key_from_hex(key_hex)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid key: {str(e)}")
            return
        
        # Validate IV for CBC
        iv = None
        if mode == 'CBC':
            if not iv_hex and action == 'encrypt':
                messagebox.showerror("Error", "IV is required for CBC mode encryption!\nPlease generate or enter IV.")
                return
            if iv_hex:
                try:
                    iv = read_des_iv_from_hex(iv_hex)
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid IV: {str(e)}")
                    return
        
        # Disable button
        self.des_execute_btn.configure(state="disabled", text="⏳ Processing...")
        self.des_result_text.delete("1.0", "end")
        self.des_result_text.insert("1.0", f"Executing DES {action}...\n")
        
        def run_des():
            try:
                if action == 'encrypt':
                    self.des_encrypt_file(input_file, output_file, key, mode, iv)
                else:
                    self.des_decrypt_file(input_file, output_file, key, mode, iv)
                
                self.after(0, lambda: self.des_execute_btn.configure(
                    state="normal", text="🔐 Execute DES"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Execution failed:\n{str(e)}"))
                self.after(0, lambda: self.des_execute_btn.configure(
                    state="normal", text="🔐 Execute DES"))
        
        # Run in separate thread
        thread = threading.Thread(target=run_des)
        thread.daemon = True
        thread.start()
    
    def des_encrypt_file(self, input_file, output_file, key, mode, iv):
        """DES Encryption"""
        try:
            # Read plaintext
            plaintext = read_text_file(input_file).encode('utf-8')
            
            # Encrypt
            ciphertext, iv_used = self.des.encrypt(plaintext, key, mode=mode, iv=iv)
            
            # Convert to hex
            ciphertext_hex = bytes_to_hex(ciphertext)
            iv_hex = bytes_to_hex(iv_used) if iv_used else None
            
            # Save output
            save_encrypted_output(output_file, ciphertext_hex, iv_hex, mode)
            
            # Display result
            result = f"✓ Encryption Successful!\n\n"
            result += f"Mode: {mode}\n"
            result += f"Key: {bytes_to_hex(key).upper()}\n"
            if iv_hex:
                result += f"IV: {iv_hex.upper()}\n"
            result += f"Input: {input_file}\n"
            result += f"Output: {output_file}\n\n"
            result += f"Ciphertext preview (first 200 hex chars):\n{ciphertext_hex.upper()[:200]}..."
            
            self.after(0, lambda: self.des_result_text.delete("1.0", "end"))
            self.after(0, lambda: self.des_result_text.insert("1.0", result))
            
            self.after(0, lambda: messagebox.showinfo("Success", 
                f"File encrypted successfully!\n\nOutput saved to:\n{output_file}"))
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def des_decrypt_file(self, input_file, output_file, key, mode, iv):
        """DES Decryption"""
        try:
            # Parse input file
            data = parse_encrypted_input(input_file)
            
            # Get ciphertext
            ciphertext = hex_to_bytes(data['ciphertext'])
            
            # Get IV from file if not provided
            if mode == 'CBC' and iv is None:
                if data['iv']:
                    iv = hex_to_bytes(data['iv'])
                else:
                    raise ValueError("IV not found in encrypted file and not provided!")
            
            # Decrypt
            plaintext = self.des.decrypt(ciphertext, key, mode=mode, iv=iv)
            
            # Save output
            write_text_file(output_file, plaintext.decode('utf-8'))
            
            # Display result
            result = f"✓ Decryption Successful!\n\n"
            result += f"Mode: {mode}\n"
            result += f"Key: {bytes_to_hex(key).upper()}\n"
            if iv:
                result += f"IV: {bytes_to_hex(iv).upper()}\n"
            result += f"Input: {input_file}\n"
            result += f"Output: {output_file}\n\n"
            result += f"Plaintext preview (first 500 chars):\n"
            result += f"{plaintext.decode('utf-8')[:500]}..."
            
            self.after(0, lambda: self.des_result_text.delete("1.0", "end"))
            self.after(0, lambda: self.des_result_text.insert("1.0", result))
            
            self.after(0, lambda: messagebox.showinfo("Success", 
                f"File decrypted successfully!\n\nOutput saved to:\n{output_file}"))
            
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
            
    # ==================== AES FUNCTIONS ====================
    def on_aes_mode_change(self):
        """Enable/disable IV field based on mode"""
        mode = self.aes_mode_var.get()
        if mode == "CBC":
            self.aes_iv_entry.configure(state="normal")
            self.aes_iv_btn.configure(state="normal")
        else:
            self.aes_iv_entry.configure(state="normal")
            self.aes_iv_btn.configure(state="disabled")

    def generate_aes_key(self):
        """Generate random AES-128 key"""
        import secrets
        key = secrets.token_hex(16)  # 16 bytes = 32 hex chars
        self.aes_key_entry.delete(0, "end")
        self.aes_key_entry.insert(0, key.upper())
        messagebox.showinfo("Success", f"Generated Key:\n{key.upper()}")

    def generate_aes_iv(self):
        """Generate random AES IV"""
        import secrets
        iv = secrets.token_hex(16)  # 16 bytes = 32 hex chars
        self.aes_iv_entry.delete(0, "end")
        self.aes_iv_entry.insert(0, iv.upper())
        messagebox.showinfo("Success", f"Generated IV:\n{iv.upper()}")

    def execute_aes(self):
        """Execute AES encryption/decryption"""
        # Validate inputs
        mode = self.aes_mode_var.get()
        action = self.aes_action_var.get()
        input_file = self.aes_input_entry.get()
        output_file = self.aes_output_entry.get()
        key_hex = self.aes_key_entry.get().strip()
        iv_hex = self.aes_iv_entry.get().strip()
        
        if not input_file:
            messagebox.showerror("Error", "Please select input file!")
            return
        
        if not output_file:
            messagebox.showerror("Error", "Please select output file!")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist!")
            return
        
        if not key_hex:
            messagebox.showerror("Error", "Please enter key!")
            return
        
        # Validate key
        try:
            key = hex_to_bytes(key_hex)
            if len(key) != 16:
                raise ValueError(f"AES-128 key must be 16 bytes (32 hex chars), got {len(key)}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid key: {str(e)}")
            return
        
        # Validate IV for CBC
        iv = None
        if mode == 'CBC':
            if not iv_hex and action == 'encrypt':
                messagebox.showerror("Error", "IV is required for CBC mode encryption!\nPlease generate or enter IV.")
                return
            if iv_hex:
                try:
                    iv = hex_to_bytes(iv_hex)
                    if len(iv) != 16:
                        raise ValueError(f"AES IV must be 16 bytes (32 hex chars), got {len(iv)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid IV: {str(e)}")
                    return
        
        # Disable button
        self.aes_execute_btn.configure(state="disabled", text="⏳ Processing...")
        self.aes_result_text.delete("1.0", "end")
        self.aes_result_text.insert("1.0", f"Executing AES {action}...\n")
        
        def run_aes():
            try:
                if action == 'encrypt':
                    self.aes_encrypt_file(input_file, output_file, key, mode, iv)
                else:
                    self.aes_decrypt_file(input_file, output_file, key, mode, iv)
                
                self.after(0, lambda: self.aes_execute_btn.configure(
                    state="normal", text="🔐 Execute AES"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Execution failed:\n{str(e)}"))
                self.after(0, lambda: self.aes_execute_btn.configure(
                    state="normal", text="🔐 Execute AES"))
        
        # Run in separate thread
        thread = threading.Thread(target=run_aes)
        thread.daemon = True
        thread.start()

    def aes_encrypt_file(self, input_file, output_file, key, mode, iv):
        """AES Encryption"""
        try:
            # Import AES (Already imported at top, but kept for logic consistency)
            aes = AESModes()
            
            # Read plaintext
            plaintext = read_text_file(input_file).encode('utf-8')
            
            # Encrypt
            ciphertext, iv_used = aes.encrypt(plaintext, key, mode=mode, iv=iv)
            
            # Convert to hex
            ciphertext_hex = bytes_to_hex(ciphertext)
            iv_hex = bytes_to_hex(iv_used) if iv_used else None
            
            # Save output
            save_encrypted_output(output_file, ciphertext_hex, iv_hex, mode)
            
            # Display result
            result = f"✓ Encryption Successful!\n\n"
            result += f"Mode: {mode}\n"
            result += f"Key: {bytes_to_hex(key).upper()}\n"
            if iv_hex:
                result += f"IV: {iv_hex.upper()}\n"
            result += f"Input: {input_file}\n"
            result += f"Output: {output_file}\n\n"
            result += f"Ciphertext preview (first 200 hex chars):\n{ciphertext_hex.upper()[:200]}..."
            
            self.after(0, lambda: self.aes_result_text.delete("1.0", "end"))
            self.after(0, lambda: self.aes_result_text.insert("1.0", result))
            
            self.after(0, lambda: messagebox.showinfo("Success",
                f"File encrypted successfully!\n\nOutput saved to:\n{output_file}"))
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")

    def aes_decrypt_file(self, input_file, output_file, key, mode, iv):
        """AES Decryption"""
        try:
            # Import AES
            aes = AESModes()
            
            # Parse input file
            data = parse_encrypted_input(input_file)
            
            # Get ciphertext
            ciphertext = hex_to_bytes(data['ciphertext'])
            
            # Get IV from file if not provided
            if mode == 'CBC' and iv is None:
                if data['iv']:
                    iv = hex_to_bytes(data['iv'])
                else:
                    raise ValueError("IV not found in encrypted file and not provided!")
            
            # Decrypt
            plaintext = aes.decrypt(ciphertext, key, mode=mode, iv=iv)
            
            # Save output
            write_text_file(output_file, plaintext.decode('utf-8'))
            
            # Display result
            result = f"✓ Decryption Successful!\n\n"
            result += f"Mode: {mode}\n"
            result += f"Key: {bytes_to_hex(key).upper()}\n"
            if iv:
                result += f"IV: {bytes_to_hex(iv).upper()}\n"
            result += f"Input: {input_file}\n"
            result += f"Output: {output_file}\n\n"
            result += f"Plaintext preview (first 500 chars):\n"
            result += f"{plaintext.decode('utf-8')[:500]}..."
            
            self.after(0, lambda: self.aes_result_text.delete("1.0", "end"))
            self.after(0, lambda: self.aes_result_text.insert("1.0", result))
            
            self.after(0, lambda: messagebox.showinfo("Success",
                f"File decrypted successfully!\n\nOutput saved to:\n{output_file}"))
            
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    # ==================== CAESAR FUNCTIONS ====================
    
    def crack_caesar(self):
        input_file = self.caesar_input_entry.get()
        output_file = self.caesar_output_entry.get()
        
        if not input_file or not output_file:
            messagebox.showerror("Error", "Please select input and output files!")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist!")
            return
        
        # Disable button
        self.caesar_crack_btn.configure(state="disabled", text="⏳ Processing...")
        self.caesar_result_text.delete("1.0", "end")
        self.caesar_result_text.insert("1.0", "Cracking Caesar cipher...\n\n")
        
        def run_crack():
            try:
                key, plaintext = crack_caesar_file(input_file, output_file)
                self.after(0, lambda: self.update_caesar_result(key, plaintext, output_file))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to crack: {str(e)}"))
                self.after(0, lambda: self.caesar_crack_btn.configure(state="normal", text="🔓 Crack Caesar Cipher"))
        
        thread = threading.Thread(target=run_crack)
        thread.daemon = True
        thread.start()
    
    def update_caesar_result(self, key, plaintext, output_file):
        self.caesar_result_text.delete("1.0", "end")
        result = f"✓ Successfully cracked!\n\n"
        result += f"Found Key: {key}\n"
        result += f"Output saved to: {output_file}\n\n"
        result += "=" * 60 + "\n"
        result += "Plaintext Preview (first 500 characters):\n"
        result += "=" * 60 + "\n\n"
        result += plaintext[:500]
        if len(plaintext) > 500:
            result += "\n\n... (truncated)"
        
        self.caesar_result_text.insert("1.0", result)
        self.caesar_crack_btn.configure(state="normal", text="🔓 Crack Caesar Cipher")
        messagebox.showinfo("Success", "Caesar cipher cracked successfully!")
    
    # ==================== MONO FUNCTIONS ====================
    
    def crack_mono(self):
        input_file = self.mono_input_entry.get()
        output_file = self.mono_output_entry.get()
        
        if not input_file or not output_file:
            messagebox.showerror("Error", "Please select input and output files!")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist!")
            return
        
        self.mono_crack_btn.configure(state="disabled", text="⏳ Processing...")
        self.mono_result_text.delete("1.0", "end")
        self.mono_result_text.insert("1.0", "Analyzing mono-alphabetic cipher...\nThis may take a few minutes...\n\n")
        
        def run_crack():
            try:
                mapping, plaintext, score = crack_mono_file(input_file, output_file)
                self.after(0, lambda: self.update_mono_result(mapping, plaintext, score, output_file))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to crack: {str(e)}"))
                self.after(0, lambda: self.mono_crack_btn.configure(state="normal", text="🔍 Analyze & Decrypt"))
        
        thread = threading.Thread(target=run_crack)
        thread.daemon = True
        thread.start()
    
    def update_mono_result(self, mapping, plaintext, score, output_file):
        self.mono_result_text.delete("1.0", "end")
        result = f"✓ Successfully cracked!\n\n"
        result += f"Fitness Score: {score:.4f}\n"
        result += f"Output saved to: {output_file}\n\n"
        result += "=" * 60 + "\n"
        result += "Mapping (first 13 letters):\n"
        result += "=" * 60 + "\n"
        mapping_items = list(mapping.items())[:13]
        result += ', '.join([f"{k}->{v}" for k, v in mapping_items]) + "...\n\n"
        result += "=" * 60 + "\n"
        result += "Plaintext Preview (first 400 characters):\n"
        result += "=" * 60 + "\n\n"
        result += plaintext[:400]
        if len(plaintext) > 400:
            result += "\n\n... (truncated)"
        
        self.mono_result_text.insert("1.0", result)
        self.mono_crack_btn.configure(state="normal", text="🔍 Analyze & Decrypt")
        messagebox.showinfo("Success", "Mono-alphabetic cipher cracked successfully!")
    
    # ==================== VIGENERE FUNCTIONS ====================
    
    def crack_vigenere(self):
        input_file = self.vigenere_input_entry.get()
        output_file = self.vigenere_output_entry.get()
        
        if not input_file or not output_file:
            messagebox.showerror("Error", "Please select input and output files!")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist!")
            return
        
        self.vigenere_crack_btn.configure(state="disabled", text="⏳ Processing...")
        self.vigenere_result_text.delete("1.0", "end")
        self.vigenere_result_text.insert("1.0", "Cracking Vigenère cipher...\nAnalyzing key length...\n\n")
        
        def run_crack():
            try:
                key, plaintext = crack_vigenere_file(input_file, output_file)
                self.after(0, lambda: self.update_vigenere_result(key, plaintext, output_file))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to crack: {str(e)}"))
                self.after(0, lambda: self.vigenere_crack_btn.configure(state="normal", text="🔑 Crack Vigenère"))
        
        thread = threading.Thread(target=run_crack)
        thread.daemon = True
        thread.start()
    
    def update_vigenere_result(self, key, plaintext, output_file):
        self.vigenere_result_text.delete("1.0", "end")
        result = f"✓ Successfully cracked!\n\n"
        result += f"Found Key: {key}\n"
        result += f"Key Length: {len(key)}\n"
        result += f"Output saved to: {output_file}\n\n"
        result += "=" * 60 + "\n"
        result += "Plaintext Preview (first 500 characters):\n"
        result += "=" * 60 + "\n\n"
        result += plaintext[:500]
        if len(plaintext) > 500:
            result += "\n\n... (truncated)"
        
        self.vigenere_result_text.insert("1.0", result)
        self.vigenere_crack_btn.configure(state="normal", text="🔑 Crack Vigenère")
        messagebox.showinfo("Success", "Vigenère cipher cracked successfully!")
    
    # ==================== HELPER FUNCTIONS ====================
    
    def browse_file(self, entry_widget):
        filename = filedialog.askopenfilename(
            title="Select file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, filename)
    
    def save_file(self, entry_widget):
        filename = filedialog.asksaveasfilename(
            title="Save file",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, filename)
    
    # ==================== CLEAR FUNCTIONS ====================
    
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
        """Clear AES tab"""
        self.aes_input_entry.delete(0, "end")
        self.aes_output_entry.delete(0, "end")
        self.aes_key_entry.delete(0, "end")
        self.aes_iv_entry.delete(0, "end")
        self.aes_result_text.delete("1.0", "end")


if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()