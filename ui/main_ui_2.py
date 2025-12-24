import sys
import os
import subprocess
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QMessageBox, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QCursor, QColor

class ProcessMonitor(QObject):
    """Monitor khi tiến trình con kết thúc"""
    process_finished = pyqtSignal()
    
    def __init__(self, process):
        super().__init__()
        self.process = process
        
    def monitor(self):
        self.process.wait()
        self.process_finished.emit()

class MainMenuUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Encryption Toolkit")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #e5e7eb;")  # Nền xám nhạt giống UI Playfair/RSA
        
        self.active_processes = []
        self.init_ui()
        
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(0)
        
        # --- MAIN CARD (giống UI Playfair/RSA) ---
        self.card = QFrame()
        self.card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        # Shadow effect giống UI Playfair/RSA
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
        header = QLabel("🔐 Encryption Toolkit")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 32px; font-weight: bold; color: #1f2937; margin-bottom: 10px; border: none;")
        card_layout.addWidget(header)

        # Subtitle
        subtitle = QLabel("Select an encryption algorithm to begin")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 18px; color: #6b7280; margin-bottom: 40px; border: none;")
        card_layout.addWidget(subtitle)

        # Cards container
        cards_container = QHBoxLayout()
        cards_container.setSpacing(30)
        cards_container.setContentsMargins(20, 0, 20, 0)
        
        # Playfair Card
        playfair_card = self.create_card(
            "Playfair Cipher",
            "Classical symmetric encryption using matrix technique",
            "🎭",
            "#3b82f6",  # Xanh dương
            "#2563eb"   # Xanh dương đậm hơn
        )
        playfair_card.mousePressEvent = lambda e: self.open_playfair()
        cards_container.addWidget(playfair_card)
        
        # RSA Card
        rsa_card = self.create_card(
            "RSA Encryption",
            "Modern asymmetric encryption using public-private keys",
            "🔐",
            "#10b981",  # Xanh lá
            "#059669"   # Xanh lá đậm hơn
        )
        rsa_card.mousePressEvent = lambda e: self.open_rsa()
        cards_container.addWidget(rsa_card)
        
        card_layout.addLayout(cards_container)
        
        # Spacer
        spacer = QLabel("")
        spacer.setFixedHeight(30)
        card_layout.addWidget(spacer)
        
        # Footer text
        footer_label = QLabel("Click on any card to open the corresponding encryption tool")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("font-size: 14px; color: #9ca3af; border: none;")
        card_layout.addWidget(footer_label)
        
        # Copyright
        copyright_label = QLabel("© 2024 Encryption Toolkit - Cryptography Lab")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("font-size: 12px; color: #9ca3af; margin-top: 10px; border: none;")
        card_layout.addWidget(copyright_label)
        
        card_layout.addStretch()
        
    def create_card(self, title, description, icon, color, hover_color):
        card = QFrame()
        card.setFixedSize(450, 320)
        card.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Shadow effect cho card
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(15)
        card_shadow.setColor(QColor(0, 0, 0, 20))
        card_shadow.setOffset(0, 3)
        card.setGraphicsEffect(card_shadow)
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e5e7eb;
            }}
            QFrame:hover {{
                border: 2px solid {color};
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(15)
        
        # Icon với background tròn
        icon_container = QFrame()
        icon_container.setFixedSize(80, 80)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 40px;
                border: none;
            }}
        """)
        
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                background: transparent;
                border: none;
                color: white;
            }
        """)
        icon_layout.addWidget(icon_label)
        
        card_layout.addWidget(icon_container, 0, Qt.AlignHCenter)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #1f2937;
                background: transparent;
                border: none;
                margin-top: 5px;
            }
        """)
        card_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #6b7280;
                background: transparent;
                border: none;
                margin-top: 5px;
            }
        """)
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)
        
        card_layout.addStretch()
        
        # Button style indicator (giống nút trong UI Playfair/RSA)
        indicator = QPushButton("Open Tool")
        indicator.setCursor(QCursor(Qt.PointingHandCursor))
        indicator.setFixedHeight(40)
        indicator.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
        indicator.clicked.connect(lambda: None)  # Chỉ để hiển thị, sự kiện thực tế ở card level
        
        card_layout.addWidget(indicator)
        
        return card
    
    def open_playfair(self):
        """Open Playfair Cipher application"""
        try:
            # Path to playfair_ui.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            playfair_path = os.path.join(current_dir, "playfair_ui.py")
            
            # Check if file exists
            if not os.path.exists(playfair_path):
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Cannot find Playfair UI file:\n{playfair_path}"
                )
                return
            
            # Open Playfair UI in a new process
            process = subprocess.Popen([sys.executable, playfair_path])
            self.active_processes.append(process)
            
            # Monitor when the process finishes
            monitor = ProcessMonitor(process)
            monitor.process_finished.connect(self.show_main_window)
            
            # Start monitoring in a separate thread
            thread = threading.Thread(target=monitor.monitor)
            thread.daemon = True
            thread.start()
            
            # Hide main window
            self.hide()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Cannot open Playfair Cipher:\n{str(e)}"
            )
    
    def open_rsa(self):
        """Open RSA Encryption application"""
        try:
            # Path to rsa_ui.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            rsa_path = os.path.join(current_dir, "rsa_ui.py")
            
            # Check if file exists
            if not os.path.exists(rsa_path):
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Cannot find RSA UI file:\n{rsa_path}"
                )
                return
            
            # Open RSA UI in a new process
            process = subprocess.Popen([sys.executable, rsa_path])
            self.active_processes.append(process)
            
            # Monitor when the process finishes
            monitor = ProcessMonitor(process)
            monitor.process_finished.connect(self.show_main_window)
            
            # Start monitoring in a separate thread
            thread = threading.Thread(target=monitor.monitor)
            thread.daemon = True
            thread.start()
            
            # Hide main window
            self.hide()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Cannot open RSA Encryption:\n{str(e)}"
            )
    
    def show_main_window(self):
        """Show main window when child application is closed"""
        # Clean up finished processes
        self.active_processes = [p for p in self.active_processes if p.poll() is None]
        
        # Show main window and bring to front
        self.show()
        self.raise_()
        self.activateWindow()
    
    def closeEvent(self, event):
        """Handle main window close event"""
        # Check if there are any active processes
        active = [p for p in self.active_processes if p.poll() is None]
        
        if active:
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "There are still running encryption tools. Do you want to close them all and exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Terminate all active processes
                for process in active:
                    try:
                        process.terminate()
                        process.wait(timeout=2)
                    except:
                        pass
                event.accept()
            else:
                event.ignore()
        else:
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Are you sure you want to exit Encryption Toolkit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

def main():
    app = QApplication(sys.argv)
    
    # Set application font (giống UI Playfair/RSA)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Set application style (giống UI Playfair/RSA)
    app.setStyleSheet("""
        QMessageBox {
            background-color: white;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }
        QMessageBox QLabel {
            color: #1f2937;
            font-size: 14px;
        }
        QMessageBox QPushButton {
            background-color: #3b82f6;
            color: black;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #2563eb;
            color: black;
        }
    """)
    
    window = MainMenuUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()