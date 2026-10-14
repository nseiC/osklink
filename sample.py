from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit, QHBoxLayout, QMessageBox
from numpy import logspace, log10
import datetime
import os
import time
import pandas as pd

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
        self.archive = self.resolve_archive(self.arquivo.text.text())

    @staticmethod
    def resolve_archive(path):
        """Aceita um arquivo ou uma pasta. Se for pasta (ou vazio), cria um arquivo
        com data e hora dentro dela."""
        path = os.path.expanduser(path.strip()) or os.path.join(os.path.expanduser("~"), "OscLink", "")
        if os.path.isdir(path) or path.endswith(os.sep):
            stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            path = os.path.join(path, f"ensaio_{stamp}.txt")
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        return path

    def compute_frequencies(self):
        self.array_of_frequencies = logspace(log10(self.initial_frequency),
                                             log10(self.final_frequency),
                                             self.number_of_samples, endpoint=True, base=10)

    def terminal_execution(self):
        self.get_values()
        self.compute_frequencies()
        self.generator.open_channel()
        self.generator.set_amplitude(self.initial_voltage)

        df_final = pd.DataFrame()

        for f in self.array_of_frequencies:
            self.generator.set_frequency(f)
            self.generator.beep()
            self.scope.set_scale(f)
            self.scope.set_voltage_scale_generic("CH1")
            self.scope.set_voltage_scale_generic("CH2")
            time.sleep(1)

        # captura das formas de onda
            times1, voltages1 = self.scope.capture_waveform(ch="CH1", frequency=f, filename=self.archive, append=True)
            times2, voltages2 = self.scope.capture_waveform(ch="CH2", frequency=f, filename=self.archive, append=True)

        # garantir mesmo tamanho
            min_len = min(len(times1), len(times2))
            times1, voltages1, voltages2 = times1[:min_len], voltages1[:min_len], voltages2[:min_len]

        # dataframe para esta frequência
            df_freq = pd.DataFrame({
                f"tempo({f:.1f}Hz)": times1,
                f"CH1({f:.1f}Hz)": voltages1,
                f"CH2({f:.1f}Hz)": voltages2
            })

        # concatena lado a lado
            if df_final.empty:
                df_final = df_freq
            else:
                df_final = pd.concat([df_final, df_freq], axis=1)



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
        try:
            self.mypage.terminal_execution()
        except Exception as e:
            QMessageBox.critical(self, "Erro no ensaio", f"{type(e).__name__}: {e}")
            raise
        QMessageBox.information(self, "Ensaio concluído", f"Formas de onda salvas em:\n{self.mypage.archive}")
