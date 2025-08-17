from PyQt5.QtWidgets import (QWidget, QLabel, QLayout, QVBoxLayout, QLineEdit)

class sample_page(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Amostragem")
        self.resize(750, 750)

            # Criando um label central
        self.label = QLabel("Amostragem", self)
        self.mylayout = QVBoxLayout()
        self.mylayout.addWidget(self.label)
        self.setLayout(self.mylayout)
        