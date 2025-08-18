import pyvisa
import serial.tools.list_ports 
from PyQt5.QtWidgets import (QWidget, QLabel, QLayout, QVBoxLayout, QHBoxLayout, QPushButton,
QComboBox)

class serial_page(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Serial")
        self.resize(750, 750)

            # Criando um label central
        self.scope = device_option("Osciloscópio")
        self.generator = device_option("Gerador de funções")
        self.dso2d15 = device_option("DSO2D15")
        self.arduino = device_option("Arduino")
        self.applybtn = QPushButton("Conectar")
        
        self.mylayout = QVBoxLayout()
        self.mylayout.addWidget(self.scope)
        self.mylayout.addWidget(self.generator)
        self.mylayout.addWidget(self.applybtn)
        self.setLayout(self.mylayout)
        
            
class device_option(QWidget):
    def __init__(self,mystr):
        super().__init__()
        self.mystr=mystr
        self.myObj = QHBoxLayout()
        self.mydevice = QLabel(self.mystr)
        self.mybtn = QComboBox()
        if mystr == 'Osciloscópio':
            rm = pyvisa.ResourceManager()
            self.mybtn.addItem(rm.list_resources()[0])
        if mystr == 'Gerador de funções':
            porta = serial.tools.list_ports.comports()
            self.mybtn.addItem(porta[0].device)
        self.myObj.addWidget(self.mydevice)
        self.myObj.addWidget(self.mybtn)
        self.setLayout(self.myObj)