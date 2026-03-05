import uuid
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QWidget, QGraphicsBlurEffect, QStackedWidget, QMessageBox)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QIcon

from core.config import config
from core.auth import authenticate_elyby, authenticate_microsoft

def resource_path(relative_path):
    import sys
    try:
        base_path = sys._MEIPASS
    except Exception:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(800, 500)
        self.old_pos = None
        
        self.init_ui()
        
    def init_ui(self):
        # Base Widget
        self.base_widget = QWidget(self)
        self.base_widget.setGeometry(0, 0, 800, 500)
        self.base_widget.setStyleSheet("background-color: #0f0f13; border-radius: 15px;")
        
        # Background Image
        self.bg_label = QLabel(self.base_widget)
        self.bg_label.setGeometry(0, 0, 800, 500)
        self.bg_label.setStyleSheet("border-radius: 15px;")
        self.bg_label.setScaledContents(True)
        
        bg_path = resource_path("bg.jpg")
        if os.path.exists(bg_path):
            self.bg_label.setPixmap(QPixmap(bg_path))
            
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(15)
        self.bg_label.setGraphicsEffect(self.blur_effect)
        
        # Overlay
        self.overlay = QWidget(self.base_widget)
        self.overlay.setGeometry(0, 0, 800, 500)
        self.overlay.setStyleSheet("background-color: rgba(15, 15, 19, 0.75); border-radius: 15px;")
        
        main_layout = QVBoxLayout(self.overlay)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Title Bar
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("background-color: rgba(0, 0, 0, 0.4); border-top-left-radius: 15px; border-top-right-radius: 15px;")
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)
        
        title_label = QLabel("Horizon-Drift - Login")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px; background: transparent;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        close_btn = QPushButton("X")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("QPushButton { background: transparent; color: white; border: none; font-weight: bold; } QPushButton:hover { background: #ef4444; border-radius: 15px; }")
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)
        
        main_layout.addWidget(self.title_bar)
        
        # Content Layout
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(40, 40, 40, 40)
        
        # Left Side - Login Box
        login_box = QWidget()
        login_box.setFixedWidth(350)
        login_box.setStyleSheet("background-color: rgba(0, 0, 0, 0.6); border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);")
        login_layout = QVBoxLayout(login_box)
        login_layout.setContentsMargins(30, 30, 30, 30)
        login_layout.setSpacing(15)
        
        welcome_label = QLabel("Welcome Back")
        welcome_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; background: transparent; border: none;")
        welcome_label.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(welcome_label)
        
        # Auth Type Selection
        auth_type_layout = QHBoxLayout()
        self.auth_buttons = []
        
        self.btn_offline = QPushButton("Offline")
        self.btn_elyby = QPushButton("Ely.by")
        self.btn_microsoft = QPushButton("Microsoft")
        
        for idx, btn in enumerate([self.btn_offline, self.btn_elyby, self.btn_microsoft]):
            btn.setCheckable(True)
            btn.setFixedHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.7); border-radius: 5px; font-weight: bold; border: none;
                }
                QPushButton:hover { background: rgba(255,255,255,0.1); color: white; }
                QPushButton:checked { background: #4f46e5; color: white; }
            """)
            btn.clicked.connect(lambda checked, i=idx: self.switch_auth_type(i))
            self.auth_buttons.append(btn)
            auth_type_layout.addWidget(btn)
            
        login_layout.addLayout(auth_type_layout)
        
        # Input Fields
        self.input_stack = QStackedWidget()
        self.input_stack.setStyleSheet("background: transparent; border: none;")
        
        # 0: Offline
        offline_widget = QWidget()
        offline_layout = QVBoxLayout(offline_widget)
        offline_layout.setContentsMargins(0, 10, 0, 0)
        self.offline_user = QLineEdit()
        self.offline_user.setPlaceholderText("Username")
        self.offline_user.setFixedHeight(40)
        self.offline_user.setStyleSheet("background: rgba(255,255,255,0.1); color: white; border-radius: 5px; padding: 0 10px; font-size: 14px;")
        offline_layout.addWidget(self.offline_user)
        offline_layout.addStretch()
        self.input_stack.addWidget(offline_widget)
        
        # 1: Ely.by
        elyby_widget = QWidget()
        elyby_layout = QVBoxLayout(elyby_widget)
        elyby_layout.setContentsMargins(0, 10, 0, 0)
        self.elyby_user = QLineEdit()
        self.elyby_user.setPlaceholderText("Email or Username")
        self.elyby_user.setFixedHeight(40)
        self.elyby_user.setStyleSheet("background: rgba(255,255,255,0.1); color: white; border-radius: 5px; padding: 0 10px; font-size: 14px;")
        self.elyby_pass = QLineEdit()
        self.elyby_pass.setPlaceholderText("Password")
        self.elyby_pass.setEchoMode(QLineEdit.Password)
        self.elyby_pass.setFixedHeight(40)
        self.elyby_pass.setStyleSheet("background: rgba(255,255,255,0.1); color: white; border-radius: 5px; padding: 0 10px; font-size: 14px;")
        elyby_layout.addWidget(self.elyby_user)
        elyby_layout.addWidget(self.elyby_pass)
        elyby_layout.addStretch()
        self.input_stack.addWidget(elyby_widget)
        
        # 2: Microsoft
        ms_widget = QWidget()
        ms_layout = QVBoxLayout(ms_widget)
        ms_layout.setContentsMargins(0, 10, 0, 0)
        ms_label = QLabel("Click Login to authenticate with Microsoft via your browser.")
        ms_label.setWordWrap(True)
        ms_label.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 14px;")
        ms_label.setAlignment(Qt.AlignCenter)
        ms_layout.addWidget(ms_label)
        ms_layout.addStretch()
        self.input_stack.addWidget(ms_widget)
        
        login_layout.addWidget(self.input_stack)
        
        # Login Button
        self.login_btn = QPushButton("Login")
        self.login_btn.setFixedHeight(45)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: #4f46e5; color: white; border-radius: 5px; font-weight: bold; font-size: 16px; border: none;
            }
            QPushButton:hover { background: #4338ca; }
            QPushButton:disabled { background: #3730a3; color: rgba(255,255,255,0.5); }
        """)
        self.login_btn.clicked.connect(self.do_login)
        login_layout.addWidget(self.login_btn)
        
        content_layout.addStretch()
        content_layout.addWidget(login_box)
        content_layout.addStretch()
        
        main_layout.addLayout(content_layout)
        
        # Default to Offline
        self.switch_auth_type(0)
        
    def switch_auth_type(self, index):
        self.current_auth_type = index
        for i, btn in enumerate(self.auth_buttons):
            btn.setChecked(i == index)
        self.input_stack.setCurrentIndex(index)
        
    def do_login(self):
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Logging in...")
        
        try:
            if self.current_auth_type == 0:
                # Offline
                username = self.offline_user.text().strip()
                if not username:
                    raise ValueError("Username cannot be empty")
                
                acc = {
                    "type": "offline",
                    "username": username,
                    "uuid": str(uuid.uuid4())
                }
                self.save_account(acc)
                
            elif self.current_auth_type == 1:
                # Ely.by
                username = self.elyby_user.text().strip()
                password = self.elyby_pass.text()
                if not username or not password:
                    raise ValueError("Username and password cannot be empty")
                
                acc = authenticate_elyby(username, password)
                self.save_account(acc)
                
            elif self.current_auth_type == 2:
                # Microsoft
                self.do_microsoft_login()
                return # do_microsoft_login handles the rest
                
        except Exception as e:
            QMessageBox.critical(self, "Login Error", str(e))
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Login")
            
    def save_account(self, acc):
        accounts = config.get("accounts", [])
        accounts.append(acc)
        config.set("accounts", accounts)
        config.set("selected_account_index", len(accounts) - 1)
        self.accept()
        
    def do_microsoft_login(self):
        try:
            acc = authenticate_microsoft()
            self.save_account(acc)
        except Exception as e:
            QMessageBox.critical(self, "Login Error", str(e))
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Login")
        
    # --- Window Dragging Logic ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() < 40:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
