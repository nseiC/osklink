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
        self.mylayout.addWidget(self.dso2d15)
        self.mylayout.addWidget(self.arduino)
        self.mylayout.addWidget(self.applybtn)
        self.setLayout(self.mylayout)
        
    def list_ports(self):
        """Lista as portas VISA disponíveis e atualiza o ComboBox"""
        try:
            resources = self.rm.list_resources()
            self.combo_ports.clear()  # limpa lista antiga
            if resources:
                self.combo_ports.addItems(resources)
            else:
                self.combo_ports.addItem("Nenhuma porta encontrada")
        except Exception as e:
            self.combo_ports.clear()
            self.combo_ports.addItem(f"Erro: {e}")
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