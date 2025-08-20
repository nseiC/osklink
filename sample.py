from PyQt5.QtWidgets import (QWidget, QPushButton ,QLabel, QLayout, QVBoxLayout, QLineEdit, QHBoxLayout)
from numpy import logspace,log10
import threading

class sample_page(QWidget):
    def __init__(self,main_page):
        super().__init__()
        self.main_page = main_page
        self.setWindowTitle("Amostragem")
        self.resize(750, 750)

        self.samples = sample_option("Amostras")
        self.vin = sample_option("Tensão de entrada")
        self.f1 = sample_option("Frequência inicial")
        self.f2 = sample_option("Frequência final")
        self.buttons = sample_buttons(self)
            # Criando um label central
        self.label = QLabel("Menu de amostragem", self)
        self.mylayout = QVBoxLayout()
        self.mylayout.addWidget(self.label)
        self.mylayout.addWidget(self.samples)
        self.mylayout.addWidget(self.vin)
        self.mylayout.addWidget(self.f1)
        self.mylayout.addWidget(self.f2)
        self.mylayout.addWidget(self.buttons)
        
        self.generator = generator(self.main_page.serial_page.mygenerator)
        
        
        self.setLayout(self.mylayout)
    
    def get_values(self):
        self.number_of_samples = self.samples.text.text()
        self.initial_voltage = self.vin.text.text()
        self.initial_frequency = self.f1.text.text()
        self.final_frequency = self.f2.text.text()
        
    def compute_frequencies(self):
        self.array_of_frequencies = logspace(log10(float(self.initial_frequency)),log10(float(self.final_frequency)),int(self.number_of_samples),endpoint=True,base=10)
        
    def terminal_execution(self):
        self.get_values()
        self.compute_frequencies()
        #while(1):
            #return
        #print(f"Numero de amostras,{self.number_of_samples}\n")
        #print(f"Frequencias,{self.array_of_frequencies}\n")
        
class sample_option(QWidget):
    def __init__(self,mystr):
        super().__init__()
        self.mystr=mystr
        self.bar = QHBoxLayout()
        self.label = QLabel(self.mystr)
        self.text = QLineEdit()
        self.text.setFixedSize(200, 40)
        self.bar.addWidget(self.label)
        self.bar.addWidget(self.text)
        self.setLayout(self.bar)
        
class sample_buttons(QWidget):
    def __init__(self,mypage):
        super().__init__()
        self.mypage=mypage
        self.bar = QHBoxLayout()
        self.start = QPushButton("Iniciar")
        self.pause = QPushButton("Pausar")
        self.stop = QPushButton("Terminar")
        self.bar.addWidget(self.start)
        self.bar.addWidget(self.pause)
        self.bar.addWidget(self.stop)
        self.setLayout(self.bar)
        
        self.start.clicked.connect(self.start_sample)
        
    def start_sample(self):
        self.mypage.terminal_execution()
        
class generator():
    def __init__(self,generator):
        super().__init__()
        self.generator = generator
        self.generator_settings = {
            "set_sine":"SOURce1:FUNCtion SINesoid", #seta CH1 para senoide
            "set_frequency": "SOURce1:FREQuency", #seguido disso, vem a frequência
            "set_amplitude": "SOURce1:VOLTage", # seguido disso, vem a amplitude
            "allow_channel_1": "OUTPut1 ON'",
            "beep":"SYSTem:BEEPer:IMMediate"
        }
        
    
    
    