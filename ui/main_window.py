import sys
import os
import urllib.request
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QStackedWidget, QGraphicsBlurEffect, QGraphicsOpacityEffect,
                             QSystemTrayIcon, QMenu, QAction, QStyle)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QColor, QFont

from ui.pages.home import HomePage
from ui.pages.settings import SettingsPage
from ui.pages.accounts import AccountsPage
from ui.pages.installations import InstallationsPage
from ui.pages.modpacks import ModpacksPage
from ui.pages.mods import ModsPage
from ui.pages.logs import LogsPage

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev, PyInstaller, and py2exe """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        if getattr(sys, 'frozen', False):
            # py2exe or cx_Freeze
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class HorizonDriftLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1024, 600)
        self.old_pos = None
        
        self.init_ui()
        
        # System Tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        tray_menu = QMenu()
        restore_action = QAction("Restore Horizon-Drift", self)
        restore_action.triggered.connect(self.showNormal)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        
        tray_menu.addAction(restore_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def init_ui(self):
        # Base container for rounded corners
        self.base_widget = QWidget(self)
        self.base_widget.setStyleSheet("background-color: #0f0f13; border-radius: 15px;")
        self.setCentralWidget(self.base_widget)
        
        base_layout = QVBoxLayout(self.base_widget)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(0)

        # Background Image Label
        self.bg_label = QLabel(self.base_widget)
        self.bg_label.setGeometry(0, 0, 1024, 600)
        self.bg_label.setStyleSheet("border-radius: 15px;")
        self.bg_label.setScaledContents(True)
        
        # Blur effect for glassmorphism
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(20)
        self.bg_label.setGraphicsEffect(self.blur_effect)
        
        # Load static background
        bg_path = resource_path("bg.jpg")
        if os.path.exists(bg_path):
            self.bg_label.setPixmap(QPixmap(bg_path))

        # Overlay to darken background
        self.overlay = QWidget(self.base_widget)
        self.overlay.setGeometry(0, 0, 1024, 600)
        self.overlay.setStyleSheet("background-color: rgba(15, 15, 19, 0.7); border-radius: 15px;")

        # Main Layout (on top of overlay)
        main_layout = QVBoxLayout(self.overlay)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Custom Title Bar
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("background-color: rgba(0, 0, 0, 0.4); border-top-left-radius: 15px; border-top-right-radius: 15px;")
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)
        
        title_label = QLabel("Horizon-Drift")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px; background: transparent;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        close_btn = QPushButton("X")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("QPushButton { background: transparent; color: white; border: none; font-weight: bold; } QPushButton:hover { background: #ef4444; border-radius: 15px; }")
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)
        
        main_layout.addWidget(self.title_bar)

        # Content Area (Sidebar + StackedWidget)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); border-bottom-left-radius: 15px; border-right: 1px solid rgba(255,255,255,0.05);")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(5)

        self.nav_buttons = []
        nav_items = [
            ("Home", 0), ("Installations", 1), ("Modpacks", 2), 
            ("Mods", 3), ("Accounts", 4), ("Settings", 5), ("Logs", 6)
        ]

        for name, index in nav_items:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    color: rgba(255,255,255,0.7); text-align: left; padding-left: 15px;
                    background: transparent; border-radius: 8px; border: none; font-size: 14px; font-weight: bold;
                }
                QPushButton:hover { background: rgba(255,255,255,0.1); color: white; }
                QPushButton:checked { background: rgba(79, 70, 229, 0.4); color: white; border-left: 4px solid #4f46e5; }
            """)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
        sidebar_layout.addStretch()
        content_layout.addWidget(self.sidebar)

        # Stacked Widget for Pages
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        
        # Add Pages
        self.stack.addWidget(HomePage(self))
        self.stack.addWidget(InstallationsPage())
        self.stack.addWidget(ModpacksPage())
        self.stack.addWidget(ModsPage())
        self.stack.addWidget(AccountsPage())
        self.stack.addWidget(SettingsPage())
        self.stack.addWidget(LogsPage())

        # Opacity effect for animations
        self.opacity_effect = QGraphicsOpacityEffect()
        self.stack.setGraphicsEffect(self.opacity_effect)
        
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

        content_layout.addWidget(self.stack)
        main_layout.addLayout(content_layout)
        
        # Set initial state
        self.nav_buttons[0].setChecked(True)

    def switch_page(self, index):
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
            
        # Animate fade out
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.finished.disconnect() if self.anim.receivers(self.anim.finished) > 0 else None
        
        def on_fade_out():
            self.stack.setCurrentIndex(index)
            self.anim.setStartValue(0.0)
            self.anim.setEndValue(1.0)
            self.anim.finished.disconnect()
            self.anim.start()
            
        self.anim.finished.connect(on_fade_out)
        self.anim.start()

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
