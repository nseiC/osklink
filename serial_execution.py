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
        self.scope_options = device_option("Osciloscópio")
        self.generator_options = device_option("Gerador de funções")
        
        self.generator = generator()
        
        self.applybtn = QPushButton("Conectar")
        
        self.mylayout = QVBoxLayout()
        self.mylayout.addWidget(self.scope_options)
        self.mylayout.addWidget(self.generator_options)
        self.mylayout.addWidget(self.applybtn)
        self.setLayout(self.mylayout)
        self.applybtn.clicked.connect(self.connect_to_devices)
        
    
    def connect_to_devices(self):
        self.rm = pyvisa.ResourceManager()
        self.myscope=self.rm.open_resource(self.scope_options.mybtn.currentText())
        idn = self.myscope.query("*IDN?")
        print("Resposta do dispositivo:", idn)
        self.generator.serial = serial.Serial(self.generator_options.mybtn.currentText(), baudrate=115200, timeout=1)
        self.generator.beep()
        #self.generator.write('SYSTem:BEEPer:IMMediate\n'.encode())
        
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
        
class generator():
    def __init__(self):
        super().__init__()
        self.serial = []
        self.settings = {
            "set_sine":"SOURce1:FUNCtion SINesoid", #seta CH1 para senoide
            "set_frequency": b"SOURce1:FREQuency", #seguido disso, vem a frequência
            "set_amplitude": b"SOURce1:VOLTage", # seguido disso, vem a amplitude
            "allow_channel_1": b"OUTPut1 ON'",
            "beep":b"SYSTem:BEEPer:IMMediate"
        }
        
    def set_frequency(self,frequency):
        self.serial.write(self.settings["set_frequency"] + b" " + str(frequency).encode() + b"\n")
        
    def beep(self):
        self.serial.write(self.settings["beep"] + b"\n")
        
    
    