from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QMessageBox, QDialog, QLineEdit
from PyQt5.QtCore import Qt
from core.config import config
from core.auth import authenticate_elyby
import uuid

class CustomFramelessDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.old_pos = None
        
        self.container = QWidget(self)
        self.container.setStyleSheet("background-color: #0f0f13; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); color: white;")
        
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title Bar
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("background-color: rgba(0, 0, 0, 0.4); border-top-left-radius: 10px; border-top-right-radius: 10px; border-bottom: none;")
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; border: none; background: transparent;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        close_btn = QPushButton("X")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("QPushButton { background: transparent; border: none; font-weight: bold; } QPushButton:hover { background: #ef4444; border-radius: 15px; }")
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)
        
        self.main_layout.addWidget(self.title_bar)
        
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.addLayout(self.content_layout)
        
    def resizeEvent(self, event):
        self.container.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() < 40:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

class AccountsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Accounts")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        layout.addWidget(title)

        # Account List
        self.account_list = QListWidget()
        self.account_list.setStyleSheet("""
            QListWidget {
                background: rgba(0,0,0,0.5);
                color: white;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.1);
                font-size: 16px;
                padding: 10px;
            }
            QListWidget::item { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); }
            QListWidget::item:selected { background: rgba(79, 70, 229, 0.5); border-radius: 5px; }
        """)
        self.account_list.currentRowChanged.connect(self.on_account_selected)
        layout.addWidget(self.account_list)

        # Buttons
        btn_layout = QHBoxLayout()
        
        add_offline_btn = QPushButton("+ Add Offline")
        add_offline_btn.setStyleSheet(self.btn_style())
        add_offline_btn.clicked.connect(self.add_offline)
        btn_layout.addWidget(add_offline_btn)

        add_ely_btn = QPushButton("+ Add Ely.by")
        add_ely_btn.setStyleSheet(self.btn_style())
        add_ely_btn.clicked.connect(self.add_elyby)
        btn_layout.addWidget(add_ely_btn)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.setStyleSheet(self.btn_style(color="#ef4444"))
        remove_btn.clicked.connect(self.remove_account)
        btn_layout.addWidget(remove_btn)

        layout.addLayout(btn_layout)
        self.refresh_list()

    def btn_style(self, color="#4f46e5"):
        return f"""
            QPushButton {{
                background: {color}; color: white; padding: 10px; border-radius: 5px; font-weight: bold;
            }}
            QPushButton:hover {{ background: rgba(255,255,255,0.2); }}
        """

    def refresh_list(self):
        self.account_list.clear()
        accounts = config.get("accounts")
        for acc in accounts:
            self.account_list.addItem(f"[{acc['type'].upper()}] {acc['username']}")
        
        idx = config.get("selected_account_index")
        if 0 <= idx < len(accounts):
            self.account_list.setCurrentRow(idx)

    def on_account_selected(self, index):
        if index >= 0:
            config.set("selected_account_index", index)

    def add_offline(self):
        dialog = CustomFramelessDialog("Add Offline Account", self)
        dialog.setFixedSize(300, 200)
        
        dialog.content_layout.addWidget(QLabel("Enter Username:"))
        user_input = QLineEdit()
        user_input.setStyleSheet("background: rgba(255,255,255,0.1); padding: 8px; border-radius: 4px;")
        dialog.content_layout.addWidget(user_input)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.setStyleSheet("background: #4f46e5; padding: 8px; border-radius: 4px; font-weight: bold;")
        add_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background: #ef4444; padding: 8px; border-radius: 4px; font-weight: bold;")
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(cancel_btn)
        dialog.content_layout.addLayout(btn_layout)
        
        if dialog.exec_() and user_input.text().strip():
            accounts = config.get("accounts")
            accounts.append({
                "type": "offline",
                "username": user_input.text().strip(),
                "uuid": str(uuid.uuid4())
            })
            config.set("accounts", accounts)
            config.set("selected_account_index", len(accounts)-1)
            self.refresh_list()

    def add_elyby(self):
        dialog = CustomFramelessDialog("Ely.by Login", self)
        dialog.setFixedSize(300, 280)
        
        dialog.content_layout.addWidget(QLabel("Email / Username:"))
        user_input = QLineEdit()
        user_input.setStyleSheet("background: rgba(255,255,255,0.1); padding: 8px; border-radius: 4px;")
        dialog.content_layout.addWidget(user_input)
        
        dialog.content_layout.addWidget(QLabel("Password:"))
        pass_input = QLineEdit()
        pass_input.setEchoMode(QLineEdit.Password)
        pass_input.setStyleSheet("background: rgba(255,255,255,0.1); padding: 8px; border-radius: 4px;")
        dialog.content_layout.addWidget(pass_input)
        
        btn_layout = QHBoxLayout()
        login_btn = QPushButton("Login")
        login_btn.setStyleSheet("background: #4f46e5; padding: 8px; border-radius: 4px; font-weight: bold;")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background: #ef4444; padding: 8px; border-radius: 4px; font-weight: bold;")
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(cancel_btn)
        dialog.content_layout.addLayout(btn_layout)
        
        def do_login():
            login_btn.setText("Logging in...")
            login_btn.setEnabled(False)
            try:
                acc = authenticate_elyby(user_input.text(), pass_input.text())
                accounts = config.get("accounts")
                accounts.append(acc)
                config.set("accounts", accounts)
                config.set("selected_account_index", len(accounts)-1)
                self.refresh_list()
                dialog.accept()
            except Exception as e:
                QMessageBox.critical(dialog, "Error", str(e))
                login_btn.setText("Login")
                login_btn.setEnabled(True)
                
        login_btn.clicked.connect(do_login)
        dialog.exec_()

    def remove_account(self):
        idx = self.account_list.currentRow()
        accounts = config.get("accounts")
        if 0 <= idx < len(accounts) and len(accounts) > 1:
            accounts.pop(idx)
            config.set("accounts", accounts)
            config.set("selected_account_index", 0)
            self.refresh_list()
        elif len(accounts) <= 1:
            QMessageBox.warning(self, "Warning", "You must have at least one account.")
