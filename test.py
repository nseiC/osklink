from PyQt5.QtWidgets import (QWidget, QLabel, QLayout, QVBoxLayout, QHBoxLayout, QPushButton,
QComboBox)

class test_page(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Teste")
        self.resize(750, 750)
       
        self.label = QLabel("Teste", self)
        self.mylayout = QVBoxLayout()
        self.mylayout.addWidget(self.label)
        self.setLayout(self.mylayout)

        
    
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