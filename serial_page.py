from PyQt5.QtWidgets import QWidget, QLabel, QLayout

class the_serial_page(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Minha Página PyQt5")
        self.resize(500, 500)

            # Criando um label central
        self.label = QLabel("Olá, Nicholas! Esta é a sua página no QMainWindow.", self)
        self.layout= QLayout()
        self.layout.setWidget(self.label)
        self.setLayout(self.layout)
        