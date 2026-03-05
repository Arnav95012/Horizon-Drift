import uuid
import minecraft_launcher_lib
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QLabel, QDialog, QLineEdit, QComboBox, QSlider, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from core.config import config, get_total_ram_mb

class VersionFetcher(QThread):
    finished = pyqtSignal(list)
    def run(self):
        try:
            versions = minecraft_launcher_lib.utils.get_version_list()
            # Filter for releases only to keep the list clean, but user asked for "every version"
            # We'll include releases and maybe snapshots if they want, but usually releases are best.
            # Let's include all releases.
            releases = [v["id"] for v in versions if v["type"] == "release"]
            if not releases:
                raise Exception("No versions found")
            self.finished.emit(releases)
        except:
            self.finished.emit(["1.21.11", "1.20.4", "1.19.4", "1.18.2", "1.16.5", "1.12.2", "1.8.9"])

class InstallationDialog(QDialog):
    def __init__(self, versions, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 420)
        self.old_pos = None
        
        self.container = QWidget(self)
        self.container.setGeometry(0, 0, 400, 420)
        self.container.setStyleSheet("background-color: #0f0f13; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); color: white;")
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title Bar
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("background-color: rgba(0, 0, 0, 0.4); border-top-left-radius: 10px; border-top-right-radius: 10px; border-bottom: none;")
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)
        
        title_label = QLabel("New Installation")
        title_label.setStyleSheet("font-weight: bold; border: none; background: transparent;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        close_btn = QPushButton("X")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("QPushButton { background: transparent; border: none; font-weight: bold; } QPushButton:hover { background: #ef4444; border-radius: 15px; }")
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)
        
        layout.addWidget(self.title_bar)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Name
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_label.setFixedWidth(80)
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("background: rgba(255,255,255,0.1); padding: 5px; border-radius: 3px;")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        content_layout.addLayout(name_layout)
        
        # Environment
        env_layout = QHBoxLayout()
        env_label = QLabel("Environment:")
        env_label.setFixedWidth(80)
        self.env_combo = QComboBox()
        self.env_combo.addItems(["vanilla", "fabric", "forge"])
        self.env_combo.setStyleSheet("background: rgba(255,255,255,0.1); padding: 5px;")
        env_layout.addWidget(env_label)
        env_layout.addWidget(self.env_combo)
        content_layout.addLayout(env_layout)
        
        # Version
        ver_layout = QHBoxLayout()
        ver_label = QLabel("Version:")
        ver_label.setFixedWidth(80)
        self.version_combo = QComboBox()
        self.version_combo.addItems(versions)
        self.version_combo.setStyleSheet("background: rgba(255,255,255,0.1); padding: 5px;")
        ver_layout.addWidget(ver_label)
        ver_layout.addWidget(self.version_combo)
        content_layout.addLayout(ver_layout)
        
        # RAM
        ram_layout = QHBoxLayout()
        self.ram_label = QLabel("RAM: 2048 MB")
        self.ram_label.setFixedWidth(80)
        self.ram_slider = QSlider(Qt.Horizontal)
        self.ram_slider.setMinimum(1024)
        self.ram_slider.setMaximum(get_total_ram_mb())
        self.ram_slider.setSingleStep(512)
        self.ram_slider.setValue(2048)
        self.ram_slider.valueChanged.connect(self.update_ram_label)
        self.ram_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; }
            QSlider::handle:horizontal { background: #4f46e5; width: 20px; margin: -6px 0; border-radius: 10px; }
        """)
        ram_layout.addWidget(self.ram_label)
        ram_layout.addWidget(self.ram_slider)
        content_layout.addLayout(ram_layout)
        
        content_layout.addStretch()
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("background: #4f46e5; padding: 8px; border-radius: 4px;")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background: #ef4444; padding: 8px; border-radius: 4px;")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        content_layout.addLayout(btn_layout)
        
        layout.addLayout(content_layout)
        
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
        
    def update_ram_label(self, val):
        val = round(val / 512) * 512
        self.ram_label.setText(f"RAM: {val} MB")
        
    def get_data(self):
        return {
            "id": str(uuid.uuid4()),
            "name": self.name_input.text() or "Unnamed",
            "type": self.env_combo.currentText(),
            "version": self.version_combo.currentText(),
            "ram_mb": round(self.ram_slider.value() / 512) * 512
        }

class InstallationsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cached_versions = ["1.21.11", "1.20.4", "1.19.4", "1.18.2", "1.16.5", "1.12.2", "1.8.9"]
        
        # Fetch versions in background
        self.fetcher = VersionFetcher()
        self.fetcher.finished.connect(self.on_versions_fetched)
        self.fetcher.start()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Installations")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background: rgba(0,0,0,0.5); color: white; border-radius: 10px; padding: 10px; font-size: 16px;")
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("+ New Installation")
        add_btn.setStyleSheet("background: #10b981; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        add_btn.clicked.connect(self.add_installation)
        
        del_btn = QPushButton("Delete Selected")
        del_btn.setStyleSheet("background: #ef4444; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        del_btn.clicked.connect(self.delete_installation)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)
        
        self.refresh_list()
        
    def on_versions_fetched(self, versions):
        if versions:
            self.cached_versions = versions
            
    def refresh_list(self):
        self.list_widget.clear()
        for inst in config.get("installations"):
            self.list_widget.addItem(f"{inst['name']} ({inst['type'].capitalize()} {inst['version']}) - {inst['ram_mb']}MB")
            
    def add_installation(self):
        dialog = InstallationDialog(self.cached_versions, self)
        if dialog.exec_():
            data = dialog.get_data()
            insts = config.get("installations")
            insts.append(data)
            config.set("installations", insts)
            self.refresh_list()
            
    def delete_installation(self):
        idx = self.list_widget.currentRow()
        insts = config.get("installations")
        if 0 <= idx < len(insts):
            if len(insts) == 1:
                QMessageBox.warning(self, "Warning", "Cannot delete the last installation.")
                return
            insts.pop(idx)
            config.set("installations", insts)
            self.refresh_list()
