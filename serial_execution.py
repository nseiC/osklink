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
        self.scope = scope()
        
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
            "allow_channel_1": b"OUTPut1 ON",
            "beep":b"SYSTem:BEEPer:IMMediate"
        }
        
    def set_frequency(self,frequency):
        self.serial.write(self.settings["set_frequency"] + b" " + str(frequency).encode() + b"\n")
        
    def beep(self):
        self.serial.write(self.settings["beep"] + b"\n")
        
    def set_amplitude(self,amplitude):
        self.serial.write(self.settings["set_amplitude"] + b" " + str(amplitude).encode() + b"\n")
        
    def open_channel(self):
        self.serial.write(self.settings["allow_channel_1"] + b"\n")
        
class scope():
    def __init__(self):
        super().__init__()
        self.serial = []
        self.settings = {
            "set_time_scale":"HORizontal:DELay:SCAle", #seta CH1 para senoide
        }
        self.time_base=[2.5e-9,5e-9,1e-8,2.5e-8,5e-8,1e-7,2.5e-7,5e-7,1e-6,2.5e-6,5e-6,1e-5,2.5e-5,5e-5,0.0001,0.00025,0.0005,0.001,0.0025,0.005,0.01,0.025,0.05,0.1,0.25,0.5,1,2.5,5,10,25,50]
        
    def set_scale(self,frequency):
        var = self.time_base[0]
        for i in range(len(self.time_base)):
            if i == 0: var = self.time_base [len(self.time_base)-1]
            else: 
                if 3*1/frequency-self.time_base[len(self.time_base)-1-i]*9<var:
                    var = self.time_base[len(self.time_base)-1-i]
                elif 3*1/frequency-self.time_base[len(self.time_base)-1-i]*9 < 0:
                    self.serial.write(self.settings["set_frequency"] + b" " + str(var).encode())
                    break