from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QProgressBar, QComboBox
from PyQt5.QtCore import Qt
from core.config import config
from core.launcher import MinecraftLauncherThread

class HomePage(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        layout.setContentsMargins(50, 50, 50, 50)

        # Title
        title = QLabel("HORIZON-DRIFT")
        title.setStyleSheet("font-family: 'Courier New', Consolas, monospace; font-size: 64px; font-weight: 900; color: white; background: transparent; letter-spacing: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Jump back into your favorite world or discover new modpacks.")
        subtitle.setStyleSheet("font-size: 18px; color: rgba(255, 255, 255, 0.7); background: transparent; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        # Controls Layout
        controls_layout = QHBoxLayout()
        controls_layout.setAlignment(Qt.AlignLeft)

        # Version Selector
        version_layout = QVBoxLayout()
        version_label = QLabel("SELECTED INSTALLATION")
        version_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 12px; font-weight: bold;")
        version_layout.addWidget(version_label)

        self.inst_combo = QComboBox()
        self.inst_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(0, 0, 0, 0.6);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                min-width: 200px;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.update_installations()
        self.inst_combo.currentIndexChanged.connect(self.on_inst_changed)
        version_layout.addWidget(self.inst_combo)
        controls_layout.addLayout(version_layout)

        controls_layout.addSpacing(20)

        # Play Button
        self.play_btn = QPushButton("PLAY")
        self.play_btn.setFixedSize(200, 65)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #4f46e5;
                border-radius: 15px;
                font-size: 28px;
                font-weight: bold;
                color: white;
                font-family: 'Courier New', Consolas, monospace;
                letter-spacing: 2px;
            }
            QPushButton:hover { background-color: #4338ca; }
            QPushButton:disabled { background-color: #3730a3; color: #a5b4fc; }
        """)
        self.play_btn.clicked.connect(self.launch_game)
        controls_layout.addWidget(self.play_btn)

        layout.addLayout(controls_layout)

        # Progress Bar (Hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(0, 0, 0, 0.5);
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #4f46e5;
                border-radius: 5px;
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 12px; font-family: 'Courier New', Consolas, monospace;")
        self.status_label.hide()
        layout.addWidget(self.status_label)

    def showEvent(self, event):
        self.update_installations()
        super().showEvent(event)

    def update_installations(self):
        self.inst_combo.blockSignals(True)
        self.inst_combo.clear()
        selected_id = config.get("selected_installation")
        idx_to_select = 0
        for i, inst in enumerate(config.get("installations")):
            self.inst_combo.addItem(f"{inst['name']} ({inst['version']})", inst["id"])
            if inst["id"] == selected_id:
                idx_to_select = i
        self.inst_combo.setCurrentIndex(idx_to_select)
        self.inst_combo.blockSignals(False)

    def on_inst_changed(self, idx):
        if idx >= 0:
            inst_id = self.inst_combo.itemData(idx)
            config.set("selected_installation", inst_id)

    def launch_game(self):
        self.play_btn.setEnabled(False)
        self.play_btn.setText("LAUNCHING...")
        self.progress_bar.show()
        self.status_label.show()
        self.progress_bar.setValue(0)
        self.launch_error = None

        inst_id = config.get("selected_installation")
        installations = config.get("installations")
        installation = next((i for i in installations if i["id"] == inst_id), installations[0])
        
        # Get selected account
        accounts = config.get("accounts")
        idx = config.get("selected_account_index")
        if not accounts or idx >= len(accounts):
            self.status_label.setText("Error: No account selected!")
            self.play_btn.setEnabled(True)
            self.play_btn.setText("PLAY")
            return
            
        account = accounts[idx]

        self.launcher_thread = MinecraftLauncherThread(installation, account)
        self.launcher_thread.progress_update.connect(self.update_progress)
        self.launcher_thread.status_update.connect(self.update_status)
        self.launcher_thread.error_update.connect(self.on_error)
        self.launcher_thread.finished.connect(self.on_launch_finished)
        self.launcher_thread.start()

    def update_progress(self, max_val, value):
        self.progress_bar.setMaximum(max_val)
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.status_label.setText(status)
        if status == "Launching Minecraft...":
            window = self.window()
            if window:
                window.hide()
        
    def on_error(self, err):
        self.launch_error = err
        self.status_label.setText(f"Error: {err}")

    def on_launch_finished(self):
        self.play_btn.setEnabled(True)
        self.play_btn.setText("PLAY")
        self.progress_bar.hide()
        if not getattr(self, 'launch_error', None):
            self.status_label.setText("Game closed.")
            
        # Restore main window
        window = self.window()
        if window:
            window.showNormal()
            window.activateWindow()
