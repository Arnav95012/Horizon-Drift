from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QLineEdit, QPushButton, QFileDialog, QCheckBox
from PyQt5.QtCore import Qt
from core.config import config, get_total_ram_mb

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        layout.addWidget(title)

        # RAM Allocation
        ram_layout = QVBoxLayout()
        self.ram_label = QLabel(f"RAM Allocation: {config.get('ram_mb')} MB")
        self.ram_label.setStyleSheet("color: white; font-size: 16px;")
        ram_layout.addWidget(self.ram_label)

        self.ram_slider = QSlider(Qt.Horizontal)
        self.ram_slider.setMinimum(1024)
        self.ram_slider.setMaximum(get_total_ram_mb())
        self.ram_slider.setSingleStep(1024)
        self.ram_slider.setValue(config.get("ram_mb"))
        self.ram_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; }
            QSlider::handle:horizontal { background: #4f46e5; width: 20px; margin: -6px 0; border-radius: 10px; }
        """)
        self.ram_slider.valueChanged.connect(self.on_ram_changed)
        ram_layout.addWidget(self.ram_slider)
        layout.addLayout(ram_layout)

        # Game Directory
        dir_layout = QVBoxLayout()
        dir_label = QLabel("Game Directory (Leave empty for default .minecraft)")
        dir_label.setStyleSheet("color: white; font-size: 16px;")
        dir_layout.addWidget(dir_label)

        dir_input_layout = QHBoxLayout()
        self.dir_input = QLineEdit(config.get("game_directory"))
        self.dir_input.setStyleSheet("background: rgba(0,0,0,0.5); color: white; padding: 10px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.1);")
        self.dir_input.textChanged.connect(lambda t: config.set("game_directory", t))
        dir_input_layout.addWidget(self.dir_input)

        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet("background: #4f46e5; color: white; padding: 10px 20px; border-radius: 5px;")
        browse_btn.clicked.connect(self.browse_directory)
        dir_input_layout.addWidget(browse_btn)
        
        dir_layout.addLayout(dir_input_layout)
        layout.addLayout(dir_layout)

        # JVM Arguments
        jvm_layout = QVBoxLayout()
        jvm_label = QLabel("JVM Arguments")
        jvm_label.setStyleSheet("color: white; font-size: 16px;")
        jvm_layout.addWidget(jvm_label)

        self.jvm_input = QLineEdit(config.get("jvm_arguments"))
        self.jvm_input.setStyleSheet("background: rgba(0,0,0,0.5); color: white; padding: 10px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.1);")
        self.jvm_input.textChanged.connect(lambda t: config.set("jvm_arguments", t))
        jvm_layout.addWidget(self.jvm_input)
        layout.addLayout(jvm_layout)
        
        # Mesa3D Toggle
        self.mesa_cb = QCheckBox("Use Mesa3D OpenGL Software Rendering (Fixes Win7 Intel HD issues)")
        self.mesa_cb.setStyleSheet("color: white; font-size: 14px; spacing: 10px;")
        self.mesa_cb.setChecked(config.get("use_mesa3d", False))
        self.mesa_cb.stateChanged.connect(lambda state: config.set("use_mesa3d", bool(state)))
        layout.addWidget(self.mesa_cb)

        layout.addStretch()

    def on_ram_changed(self, value):
        # Snap to 512MB increments
        snapped = round(value / 512) * 512
        self.ram_label.setText(f"RAM Allocation: {snapped} MB")
        config.set("ram_mb", snapped)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Game Directory")
        if directory:
            self.dir_input.setText(directory)
            config.set("game_directory", directory)
