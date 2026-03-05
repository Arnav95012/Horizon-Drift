import sys
import os

# Fix for requests/certifi in py2exe frozen environment
if getattr(sys, 'frozen', False) and not hasattr(sys, '_MEIPASS'):
    os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(os.path.dirname(sys.executable), "cacert.pem")

from PyQt5.QtWidgets import QApplication
from ui.main_window import HorizonDriftLauncher
from ui.login_dialog import LoginDialog
from core.config import config

GLOBAL_STYLE = """
QMessageBox {
    background-color: #1e1e2e;
    color: white;
}
QMessageBox QLabel {
    color: white;
}
QMessageBox QPushButton {
    background-color: #4f46e5;
    color: white;
    padding: 6px 15px;
    border-radius: 4px;
    font-weight: bold;
}
QMessageBox QPushButton:hover {
    background-color: #4338ca;
}
QComboBox QAbstractItemView {
    background-color: #1e1e2e;
    color: white;
    selection-background-color: #4f46e5;
    border: 1px solid rgba(255,255,255,0.1);
}
"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLE)
    
    # Set global font (optional, requires Inter or Segoe UI font installed)
    font = app.font()
    font.setFamily("Segoe UI")
    app.setFont(font)
    
    if not config.get("accounts"):
        login_dialog = LoginDialog()
        if login_dialog.exec_() != LoginDialog.Accepted:
            sys.exit(0)
            
    window = HorizonDriftLauncher()
    window.show()
    sys.exit(app.exec_())
