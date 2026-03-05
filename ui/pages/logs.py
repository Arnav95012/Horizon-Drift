import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
from core.config import config
import minecraft_launcher_lib

class LogsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Game Logs")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("background: rgba(0,0,0,0.8); color: #a5b4fc; font-family: monospace; border-radius: 10px; padding: 10px;")
        layout.addWidget(self.text_edit)
        
        btn = QPushButton("Refresh Logs")
        btn.setStyleSheet("background: #4f46e5; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        btn.clicked.connect(self.load_logs)
        layout.addWidget(btn)
        self.load_logs()
        
    def load_logs(self):
        custom_dir = config.get("game_directory")
        mc_dir = custom_dir if custom_dir else minecraft_launcher_lib.utils.get_minecraft_directory()
        log_path = os.path.join(mc_dir, "logs", "latest.log")
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    self.text_edit.setText(f.read())
                self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
            except Exception as e:
                self.text_edit.setText(f"Error reading logs: {e}")
        else:
            self.text_edit.setText("No logs found. Play the game first!")
