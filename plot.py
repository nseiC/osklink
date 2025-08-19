from PyQt5.QtWidgets import (QWidget, QLabel, QLayout, QVBoxLayout, QLineEdit)

class plot_page(QWidget):
    def __init__(self,main_page):
        super().__init__()
        self.main_page = main_page
        self.setWindowTitle("Geração de gráficos")
        self.resize(750, 750)

            # Criando um label central
        self.label = QLabel("Geração de gráficos", self)
        self.mylayout = QVBoxLayout()
        self.mylayout.addWidget(self.label)
        self.setLayout(self.mylayout)
        