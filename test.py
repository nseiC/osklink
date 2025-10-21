from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QMessageBox
)
import numpy as np
import sounddevice as sd
import os
import pyvisa  # pip install pyvisa


class test_page(QWidget):
    def __init__(self, main_page):
        super().__init__()
        self.main_page = main_page
        self.setWindowTitle("Teste")
        self.resize(750, 750)

        # Widgets principais
        self.label = QLabel("Página de Testes", self)
        self.btn_audio = QPushButton("🔊 Testar áudio")
        self.btn_ch1 = QPushButton("📡 Capturar forma de onda (CH1)")
        self.btn_ch2 = QPushButton("📡 Capturar forma de onda (CH2)")

        # Layout
        self.mylayout = QVBoxLayout()
        self.mylayout.addWidget(self.label)
        self.mylayout.addWidget(self.btn_audio)
        self.mylayout.addWidget(self.btn_ch1)
        self.mylayout.addWidget(self.btn_ch2)
        self.setLayout(self.mylayout)

        # Conexões
        self.btn_audio.clicked.connect(self.audio_connect)
        self.btn_ch1.clicked.connect(lambda: self.read_waveform_from_scope("CH1"))
        self.btn_ch2.clicked.connect(lambda: self.read_waveform_from_scope("CH2"))

    def audio_connect(self):
        """Gera e toca um tom senoidal de teste."""
        fs = 44100        # Taxa de amostragem (Hz)
        f = 1000          # Frequência do tom (Hz)
        duration = 3.0    # Duração em segundos
        amplitude = 0.5   # Amplitude (0 a 1)

        t = np.linspace(0, duration, int(fs * duration), endpoint=False)
        sinal = amplitude * np.sin(2 * np.pi * f * t)

        sd.play(sinal, fs)
        sd.wait()

    def read_waveform_from_scope(self, channel):
        """Lê uma forma de onda diretamente do osciloscópio Tektronix via VISA."""
        try:
            rm = pyvisa.ResourceManager()
            instruments = rm.list_resources()

            if not instruments:
                QMessageBox.warning(self, "Osciloscópio não encontrado",
                                    "Nenhum dispositivo VISA foi detectado.")
                return

            scope = rm.open_resource(instruments[0])
            scope.timeout = 10000  # 10 segundos

            idn = scope.query("*IDN?")
            print(f"📡 Conectado a: {idn.strip()}")

            # Configuração Tektronix
            scope.write(f"DATA:SOURCE {channel}")  # Canal CH1 ou CH2
            scope.write("DATA:WIDTH 1")           # 1 byte por ponto
            scope.write("DATA:ENC RPB")           # Binary positive
            scope.write("DATA:START 1")
            scope.write("DATA:STOP 2500")         # 2500 pontos

            # Lê parâmetros de escala
            ymult = float(scope.query("WFMPRE:YMULT?"))
            yzero = float(scope.query("WFMPRE:YZERO?"))
            yoff = float(scope.query("WFMPRE:YOFF?"))
            xincr = float(scope.query("WFMPRE:XINCR?"))

            # Lê dados binários
            scope.write("CURVE?")
            raw_data = scope.read_raw()

            # Remove cabeçalho (#45000...) e converte
            if raw_data.startswith(b'#'):
                header_len_digits = int(raw_data[1:2])
                header_len = 2 + header_len_digits
                data = np.frombuffer(raw_data[header_len:], dtype=np.uint8)
            else:
                raise ValueError("Formato de resposta inesperado do osciloscópio.")

            # Converte para tensão e tempo
            volts = (data - yoff) * ymult + yzero
            time = np.arange(len(volts)) * xincr

            # Diretório de salvamento
            save_dir = r"C:\Users\psei\OneDrive\Área de Trabalho\Faculdade\Sétimo 2.0\projeto_LTSPICE\Livro\FORMAS_DE_ONDA_LIVRO"
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, f"waveform_{channel}.csv")

            # Salva o arquivo
            np.savetxt(file_path, np.column_stack((time, volts)),
                       delimiter=",", header="Tempo(s),Tensão(V)", comments='')

            QMessageBox.information(
                self, "Leitura concluída",
                f"Forma de onda de {channel} salva com sucesso!\n\n{file_path}"
            )
            print(f"✅ Forma de onda {channel} salva em: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Erro na leitura",
                                 f"Ocorreu um erro ao ler o canal {channel}:\n{e}")
            print(f"❌ Erro ao ler forma de onda ({channel}):", e)


class device_option(QWidget):
    def __init__(self, mystr):
        super().__init__()
        self.mystr = mystr
        self.myObj = QHBoxLayout()
        self.mydevice = QLabel(self.mystr)
        self.mybtn = QComboBox()
        self.myObj.addWidget(self.mydevice)
        self.myObj.addWidget(self.mybtn)
        self.setLayout(self.myObj)
