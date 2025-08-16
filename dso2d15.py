from PyQt5.QtWidgets import QWidget, QLabel, QLayout, QVBoxLayout

class dso2d15_page(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("DSO2D15")
        self.resize(750, 750)

            # Criando um label central
        self.label = QLabel("DSO2D15", self)
        self.mylayout = QVBoxLayout()
        self.mylayout.addWidget(self.label)
        self.setLayout(self.mylayout)