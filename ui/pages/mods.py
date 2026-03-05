import os
import sys
import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel
from core.config import config
import minecraft_launcher_lib

class ModsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Installed Mods")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background: rgba(0,0,0,0.5); color: white; border-radius: 10px; padding: 10px; font-size: 16px;")
        layout.addWidget(self.list_widget)
        
        btn_layout = QVBoxLayout()
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.setStyleSheet("background: #4f46e5; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        refresh_btn.clicked.connect(self.load_mods)
        
        open_btn = QPushButton("Open Mods Folder")
        open_btn.setStyleSheet("background: #10b981; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        open_btn.clicked.connect(self.open_folder)
        
        layout.addWidget(refresh_btn)
        layout.addWidget(open_btn)
        self.load_mods()
        
    def get_mods_dir(self):
        custom_dir = config.get("game_directory")
        mc_dir = custom_dir if custom_dir else minecraft_launcher_lib.utils.get_minecraft_directory()
        return os.path.join(mc_dir, "mods")
        
    def load_mods(self):
        self.list_widget.clear()
        mods_dir = self.get_mods_dir()
        if os.path.exists(mods_dir):
            mods = [f for f in os.listdir(mods_dir) if f.endswith(".jar")]
            if mods:
                for f in mods:
                    self.list_widget.addItem(f)
            else:
                self.list_widget.addItem("No mods found. Add .jar files to the folder.")
        else:
            self.list_widget.addItem("Mods folder does not exist yet. Play the game first or open the folder.")
            
    def open_folder(self):
        mods_dir = self.get_mods_dir()
        os.makedirs(mods_dir, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(mods_dir)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", mods_dir])
        else:
            subprocess.Popen(["xdg-open", mods_dir])
