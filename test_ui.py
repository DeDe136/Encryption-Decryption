# test_ui.py
import sys
sys.path.append('ui')
from main_ui import CryptoApp

if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()