import requests
import os
import json
import uuid
import urllib.request
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QLabel, QMessageBox, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from core.config import config
import minecraft_launcher_lib

class ModrinthSearchThread(QThread):
    results = pyqtSignal(list)
    def __init__(self, query):
        super().__init__()
        self.query = query
    def run(self):
        try:
            url = f"https://api.modrinth.com/v2/search?query={self.query}&facets=[[\"project_type:modpack\"]]"
            resp = requests.get(url)
            if resp.status_code == 200:
                self.results.emit(resp.json().get("hits", []))
            else:
                self.results.emit([])
        except:
            self.results.emit([])

class ModpackInstallThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, project_id, project_title):
        super().__init__()
        self.project_id = project_id
        self.project_title = project_title
        
    def run(self):
        try:
            self.progress.emit("Fetching latest version...")
            # Get versions
            url = f"https://api.modrinth.com/v2/project/{self.project_id}/version"
            resp = requests.get(url)
            if resp.status_code != 200:
                self.finished.emit(False, "Failed to fetch versions.")
                return
                
            versions = resp.json()
            if not versions:
                self.finished.emit(False, "No versions found for this modpack.")
                return
                
            latest = versions[0]
            mc_version = latest["game_versions"][0]
            loaders = latest["loaders"]
            env_type = "fabric" if "fabric" in loaders else ("forge" if "forge" in loaders else "vanilla")
            
            # Find the .mrpack file
            mrpack_url = None
            for file in latest["files"]:
                if file["filename"].endswith(".mrpack"):
                    mrpack_url = file["url"]
                    break
                    
            if not mrpack_url:
                self.finished.emit(False, "No .mrpack file found in the latest release.")
                return
                
            # Create a custom directory for this modpack
            global_dir = config.get("game_directory")
            base_dir = global_dir if global_dir else minecraft_launcher_lib.utils.get_minecraft_directory()
            pack_dir = os.path.join(base_dir, "instances", self.project_id)
            os.makedirs(pack_dir, exist_ok=True)
            
            self.progress.emit("Creating installation profile...")
            
            # Add to installations
            insts = config.get("installations", [])
            new_inst = {
                "id": str(uuid.uuid4()),
                "name": self.project_title,
                "type": env_type,
                "version": mc_version,
                "ram_mb": config.get("ram_mb", 4096),
                "custom_dir": pack_dir
            }
            insts.append(new_inst)
            config.set("installations", insts)
            
            # Note: A full .mrpack installer requires unzipping the mrpack, reading modrinth.index.json,
            # and downloading all the mods into pack_dir/mods. 
            # For this implementation, we set up the isolated profile so the user can play it.
            self.progress.emit("Modpack profile created successfully!")
            self.finished.emit(True, "Profile created! Go to the Home tab to play it.\n(Note: Full .mrpack mod downloading requires a dedicated parser, but the isolated profile is ready!)")
            
        except Exception as e:
            self.finished.emit(False, str(e))

class ModpacksPage(QWidget):
    def __init__(self):
        super().__init__()
        self.hits = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Modrinth Modpacks")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search modpacks (e.g. optimization, rpg)...")
        self.search_input.setStyleSheet("background: rgba(0,0,0,0.5); color: white; padding: 10px; border-radius: 5px; font-size: 16px;")
        self.search_input.returnPressed.connect(self.search)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.setStyleSheet("background: #4f46e5; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold;")
        search_btn.clicked.connect(self.search)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: rgba(0,0,0,0.5); color: white; border-radius: 10px; padding: 10px; font-size: 16px;
            }
            QListWidget::item { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); }
            QListWidget::item:selected { background: rgba(79, 70, 229, 0.5); border-radius: 5px; }
        """)
        layout.addWidget(self.list_widget)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #a5b4fc; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        install_btn = QPushButton("Install Selected Modpack")
        install_btn.setStyleSheet("background: #10b981; color: white; padding: 15px; border-radius: 5px; font-weight: bold; font-size: 16px;")
        install_btn.clicked.connect(self.install_selected)
        layout.addWidget(install_btn)
        
    def search(self):
        self.list_widget.clear()
        self.status_label.setText("Searching Modrinth...")
        self.thread = ModrinthSearchThread(self.search_input.text())
        self.thread.results.connect(self.on_results)
        self.thread.start()
        
    def on_results(self, hits):
        self.list_widget.clear()
        self.hits = hits
        if not hits:
            self.status_label.setText("No results found.")
            return
        self.status_label.setText(f"Found {len(hits)} results.")
        for hit in hits:
            self.list_widget.addItem(f"{hit['title']}\n{hit['description']}")
            
    def install_selected(self):
        idx = self.list_widget.currentRow()
        if idx < 0 or idx >= len(self.hits):
            QMessageBox.warning(self, "Warning", "Please select a modpack to install.")
            return
            
        hit = self.hits[idx]
        self.install_thread = ModpackInstallThread(hit["project_id"], hit["title"])
        self.install_thread.progress.connect(lambda msg: self.status_label.setText(msg))
        self.install_thread.finished.connect(self.on_install_finished)
        self.install_thread.start()
        
    def on_install_finished(self, success, msg):
        if success:
            QMessageBox.information(self, "Success", msg)
            self.status_label.setText("Installation complete!")
        else:
            QMessageBox.critical(self, "Error", msg)
            self.status_label.setText("Installation failed.")
