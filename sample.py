from PyQt5.QtWidgets import (QWidget, QPushButton ,QLabel, QLayout, QVBoxLayout, QLineEdit, QHBoxLayout)
from numpy import logspace,log10
import threading
import serial
import time

class sample_page(QWidget):
    def __init__(self,main_page,generator,scope):
        super().__init__()
        self.main_page = main_page
        self.setWindowTitle("Amostragem")
        self.resize(750, 750)
        self.generator = generator
        self.scope = scope
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
        
        self.array_of_frequencies = []
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
        self.generator.open_channel()
        self.generator.set_amplitude(self.initial_voltage)
        iterator = 0
        for i in range(len(self.array_of_frequencies)):
            self.generator.set_frequency(self.array_of_frequencies[iterator])
            self.generator.beep()
            self.scope.set_scale(self.array_of_frequencies[iterator])
            time.sleep(1)
            iterator += 1
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
        
    