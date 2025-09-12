from PyQt5.QtWidgets import (QWidget, QLabel, QLayout, QVBoxLayout, QHBoxLayout, QPushButton,
QComboBox)
import numpy as np
import sounddevice as sd

class test_page(QWidget):
    def __init__(self,main_page):
        super().__init__()
        self.main_page = main_page
        self.setWindowTitle("Teste")
        self.resize(750, 750)
       
        self.label = QLabel("Teste", self)
        self.btn = QPushButton("Teste o áudio")
        self.mylayout = QVBoxLayout()
        self.mylayout.addWidget(self.label)
        self.mylayout.addWidget(self.btn)
        self.setLayout(self.mylayout)

        self.btn.clicked.connect(self.audio_connect)

    def audio_connect(self):
        # Parâmetros do sinal
        fs = 44100        # Taxa de amostragem (Hz)
        f = 1000           # Frequência do tom (Hz) -> 440 Hz = Lá padrão
        duration = 3.0    # Duração em segundos
        amplitude = 0.5   # Amplitude (0.0 a 1.0)

# Geração do vetor de tempo
        t = np.linspace(0, duration, int(fs * duration), endpoint=False)

# Sinal senoidal
        sinal = amplitude * np.sin(2 * np.pi * f * t)

# Envia para a placa de som
        sd.play(sinal, fs)

# Espera o som terminar antes de encerrar
        sd.wait()
        
    
class device_option(QWidget):
    def __init__(self,mystr):
        super().__init__()
        self.mystr=mystr
        self.myObj = QHBoxLayout()
        self.mydevice = QLabel(self.mystr)
        self.mybtn = QComboBox()
        self.myObj.addWidget(self.mydevice)
        self.myObj.addWidget(self.mybtn)
        self.setLayout(self.myObj)