from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit, QHBoxLayout
from numpy import logspace, log10
import time

class sample_page(QWidget):
    def __init__(self, main_page, generator, scope):
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
        self.arquivo = sample_option("Local do arquivo")
        self.buttons = sample_buttons(self)

        self.label = QLabel("Menu de amostragem", self)
        self.mylayout = QVBoxLayout()
        self.mylayout.addWidget(self.label)
        self.mylayout.addWidget(self.samples)
        self.mylayout.addWidget(self.vin)
        self.mylayout.addWidget(self.f1)
        self.mylayout.addWidget(self.f2)
        self.mylayout.addWidget(self.arquivo)
        self.mylayout.addWidget(self.buttons)

        self.array_of_frequencies = []
        self.setLayout(self.mylayout)

    def get_values(self):
        self.number_of_samples = int(self.samples.text.text())
        self.initial_voltage = float(self.vin.text.text())
        self.initial_frequency = float(self.f1.text.text())
        self.final_frequency = float(self.f2.text.text())
        self.archive = self.arquivo.text.text()

    def compute_frequencies(self):
        self.array_of_frequencies = logspace(log10(self.initial_frequency),
                                             log10(self.final_frequency),
                                             self.number_of_samples, endpoint=True, base=10)

    def terminal_execution(self):
        self.get_values()
        self.compute_frequencies()
        self.generator.open_channel()
        self.generator.set_amplitude(self.initial_voltage)

        voltages_list = []
        time_list = []

        for f in self.array_of_frequencies:
            self.generator.set_frequency(f)
            self.generator.beep()
            self.scope.set_scale(f)
            self.scope.set_voltage_scale_generic("CH1")
            self.scope.set_voltage_scale_generic("CH2")
            time.sleep(1)
            
            times1, voltages1 = self.scope.capture_waveform(ch="CH1", frequency=f, filename=self.archive, append=True)
            voltages_list.append(voltages1)
            time_list.append(times1)

            times2, voltages2 = self.scope.capture_waveform(ch="CH2", frequency=f, filename=self.archive, append=True)
            voltages_list.append(voltages2)
            time_list.append(times2)

        self.scope.save_waveform_cube(filename=self.archive + "a.txt",
                                      freq_list=self.array_of_frequencies,
                                      voltage_data_list=voltages_list,
                                      time_list=time_list)


class sample_option(QWidget):
    def __init__(self, mystr):
        super().__init__()
        self.bar = QHBoxLayout()
        self.label = QLabel(mystr)
        self.text = QLineEdit()
        self.text.setFixedSize(200, 40)
        self.bar.addWidget(self.label)
        self.bar.addWidget(self.text)
        self.setLayout(self.bar)


class sample_buttons(QWidget):
    def __init__(self, mypage):
        super().__init__()
        self.mypage = mypage
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
