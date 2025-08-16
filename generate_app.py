from PyQt5.QtWidgets import QMainWindow, QMenuBar, QStackedWidget, QAction
from serial import serial_page
from sample import sample_page
from dso2d15 import dso2d15_page
class generate_main(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OscLink")
        self.resize(750, 750)
                # Criação do QStackedWidget para alternar páginas
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.menu = QMenuBar()
        self.setMenuBar(self.menu)
        
        
        self.serial_page = serial_page()
        self.stack.addWidget(self.serial_page)
        self.sample_page = sample_page()
        self.stack.addWidget(self.sample_page)
        self.dso2d15_page = dso2d15_page()
        self.stack.addWidget(self.dso2d15_page)
        
        serial_action = QAction("Serial", self)
        serial_action.triggered.connect(lambda: self.stack.setCurrentIndex(0))
        self.menu.addAction(serial_action)

        # Ação Amostragem (Serial, no seu caso)
        sample_action = QAction("Amostragem", self)
        sample_action.triggered.connect(lambda: self.stack.setCurrentIndex(1))
        self.menu.addAction(sample_action)
        
        dso2d15_action = QAction("DSO2D15", self)
        dso2d15_action.triggered.connect(lambda: self.stack.setCurrentIndex(2))
        self.menu.addAction(dso2d15_action)