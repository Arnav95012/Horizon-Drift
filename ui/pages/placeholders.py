from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class PlaceholderPage(QWidget):
    def __init__(self, title_text, desc_text):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        desc = QLabel(desc_text)
        desc.setStyleSheet("font-size: 16px; color: rgba(255,255,255,0.6);")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
