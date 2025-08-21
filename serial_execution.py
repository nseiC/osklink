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
        self.scope.serial = self.myscope
        idn = self.myscope.query("*IDN?")
        #self.myscope.query("HORizontal:MAIn:SCAle 50")
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
            "set_time_scale":"HORizontal:MAIn:SCAle", #seta CH1 para senoide
            "set_voltage_scale": "CH1:SCAle",
            "min_voltage_scale": 0.005,            # limite mínimo V/div
            "max_voltage_scale": 10          
        }
        self.time_base=[2.5E-9,5E-9,1E-8,2.5E-8,5E-8,1E-7,2.5E-7,5E-7,1E-6,2.5E-6,5E-6,1E-5,2.5E-5,5E-5,0.0001,0.00025,0.0005,0.001,0.0025,0.005,0.01,0.025,0.05,0.1,0.25,0.5,1,2.5,5,10,25,50]
        
    def set_scale(self, frequency, cycles=3):
        T = 1.0 / frequency
        tb_min = (cycles * T) / 10.0
        var = next((tb for tb in self.time_base if tb >= tb_min), self.time_base[-1])
        cmd = f"{self.settings['set_time_scale']} {var:.6E}"
        print("Enviando:", cmd)
        self.serial.write(cmd)
        atual = self.serial.query("HORizontal:MAIn:SCAle?")
        print("Base atual:", atual)

    def set_voltage_scale(self, margin=1.2):
        """
        Ajusta a escala vertical do canal 1 automaticamente baseado na tensão de pico.
        margin: fator multiplicativo para garantir que o sinal caiba na tela (~20% extra)
        """
        assert self.serial is not None, "scope.serial não foi configurado"

        # 1️⃣ Lê a tensão de pico atual
        vpp_str = self.serial.query("MEASUrement:VPP? CH1")
        try:
            vpp = float(vpp_str)
        except:
            print("Erro ao ler Vpp, usando 1V como fallback")
            vpp = 1.0

        # 2️⃣ Calcula a escala necessária (10 divisões verticais na tela)
        scale = (vpp / 10) * margin

        # 3️⃣ Confere limites mínimo e máximo
        scale = max(self.settings['min_voltage_scale'], min(scale, self.settings['max_voltage_scale']))

        # 4️⃣ Envia o comando
        cmd = f"{self.settings['set_voltage_scale']} {scale:.6E}"
        print(f"Ajustando escala de tensão: Vpp={vpp:.3f}V → V/div={scale:.6E}")
        self.serial.write(cmd)

        # 5️⃣ Consulta para confirmar
        atual = self.serial.query(f"{self.settings['set_voltage_scale']}?")
        print("Escala vertical atual:", atual)
        return scale, float(atual)