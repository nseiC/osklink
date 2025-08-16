from PyQt5.QtWidgets import QMainWindow, QMenuBar
from serial_page import the_serial_page

class generate_main(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Minha Página PyQt5")
        self.resize(500, 500)
        
        self.menu = QMenuBar()
        self.setMenuBar(self.menu)
        
        pagina_serial = the_serial_page()
        menu_paginas = self.menu.addMenu(pagina_serial)
        