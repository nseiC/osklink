import pyvisa
import serial.tools.list_ports 
import time
from PyQt5.QtWidgets import (QWidget, QLabel, QLayout, QVBoxLayout, QHBoxLayout, QPushButton,
QComboBox)

class serial_page(QWidget):
    def __init__(self,main_page):
        super().__init__()
        
        self.setWindowTitle("Serial")
        self.resize(750, 750)
        self.main_page = main_page
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
        self.mygenerator = []
        self.applybtn.clicked.connect(self.connect_to_devices)
        
    
    def connect_to_devices(self):
        self.rm = pyvisa.ResourceManager()
        self.myscope=self.rm.open_resource(self.scope.mybtn.currentText())
        idn = self.myscope.query("*IDN?")
        print("Resposta do dispositivo:", idn)
        self.mygenerator = serial.Serial(self.generator.mybtn.currentText(), baudrate=115200, timeout=1)
        self.mygenerator.write('SYSTem:BEEPer:IMMediate\n'.encode())
        
class device_option(QWidget):
    def __init__(self,mystr):
        super().__init__()
        self.mystr=mystr
        self.myObj = QHBoxLayout()
        self.mydevice = QLabel(self.mystr)
        self.mybtn = QComboBox()
        self.rm = pyvisa.ResourceManager()
        if mystr == 'Osciloscópio':
            for i in range(len(self.rm.list_resources())):
                self.mybtn.addItem(self.rm.list_resources()[i])
        if mystr == 'Gerador de funções':
            portas = serial.tools.list_ports.comports()
            for j in range(len(serial.tools.list_ports.comports())):
                self.mybtn.addItem(portas[j].device)
        self.myObj.addWidget(self.mydevice)
        self.myObj.addWidget(self.mybtn)
        self.setLayout(self.myObj)
        