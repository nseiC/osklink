from PyQt5.QtWidgets import (QWidget, QPushButton ,QLabel, QLayout, QVBoxLayout, QLineEdit, QHBoxLayout)

class sample_page(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Amostragem")
        self.resize(750, 750)

        self.samples = sample_option("Amostras")
        self.vin = sample_option("Tensão de entrada")
        self.f1 = sample_option("Frequência inicial")
        self.f2 = sample_option("Frequência final")
        self.buttons = sample_buttons()
            # Criando um label central
        self.label = QLabel("Menu de amostragem", self)
        self.mylayout = QVBoxLayout()
        self.mylayout.addWidget(self.label)
        self.mylayout.addWidget(self.samples)
        self.mylayout.addWidget(self.vin)
        self.mylayout.addWidget(self.f1)
        self.mylayout.addWidget(self.f2)
        self.mylayout.addWidget(self.buttons)
        self.setLayout(self.mylayout)
        
        
class sample_option(QWidget):
    def __init__(self,mystr):
        super().__init__()
        self.mystr=mystr
        self.bar = QHBoxLayout()
        self.label = QLabel(self.mystr)
        self.text = QLineEdit()
        self.bar.addWidget(self.label)
        self.bar.addWidget(self.text)
        self.setLayout(self.bar)
        
class sample_buttons(QWidget):
    def __init__(self):
        super().__init__()
        self.bar = QHBoxLayout()
        self.start = QPushButton("Iniciar")
        self.pause = QPushButton("Pausar")
        self.stop = QPushButton("Terminar")
        self.bar.addWidget(self.start)
        self.bar.addWidget(self.pause)
        self.bar.addWidget(self.stop)
        self.setLayout(self.bar)