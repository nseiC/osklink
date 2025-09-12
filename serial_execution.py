import pyvisa
import serial.tools.list_ports 
import time
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox

class serial_page(QWidget):
    def __init__(self, main_page):
        super().__init__()
        self.setWindowTitle("Serial")
        self.resize(750, 750)
        self.main_page = main_page

        self.scope_options = device_option("Osciloscópio")
        self.generator_options = device_option("Gerador de funções")
        self.serial_device_options = device_option("Outro dispositivo serial")
        
        self.generator = generator()
        self.scope = scope()
        self.serial_device = other_serial_device()
        
        self.applybtn = QPushButton("Conectar")

        self.mylayout = QVBoxLayout()
        self.mylayout.addWidget(self.scope_options)
        self.mylayout.addWidget(self.generator_options)
        self.mylayout.addWidget(self.serial_device_options)
        self.mylayout.addWidget(self.applybtn)
        self.setLayout(self.mylayout)
        self.applybtn.clicked.connect(self.connect_to_devices)

    def connect_to_devices(self):
        self.rm = pyvisa.ResourceManager()
        self.myscope = self.rm.open_resource(self.scope_options.mybtn.currentText())
        self.scope.serial = self.myscope
        idn = self.myscope.query("*IDN?")
        print("Resposta do dispositivo:", idn)

        self.generator.serial = serial.Serial(self.generator_options.mybtn.currentText(),
                                              baudrate=115200, timeout=1)
        self.generator.beep()


class device_option(QWidget):
    def __init__(self, mystr):
        super().__init__()
        self.mystr = mystr
        self.myObj = QHBoxLayout()
        self.mydevice = QLabel(self.mystr)
        self.mybtn = QComboBox()
        self.rm = pyvisa.ResourceManager()

        if mystr == 'Osciloscópio':
            for res in self.rm.list_resources():
                self.mybtn.addItem(res)
        elif mystr == 'Gerador de funções':
            portas = serial.tools.list_ports.comports()
            for p in portas:
                self.mybtn.addItem(p.device)
        elif mystr == 'Outro dispositivo serial':
            portas = serial.tools.list_ports.comports()
            for p in portas:
                self.mybtn.addItem(p.device)
        self.myObj.addWidget(self.mydevice)
        self.myObj.addWidget(self.mybtn)
        self.setLayout(self.myObj)


class generator:
    def __init__(self):
        self.serial = None
        self.settings = {
            "set_sine": "SOURce1:FUNCtion SINesoid",
            "set_frequency": b"SOURce1:FREQuency",
            "set_amplitude": b"SOURce1:VOLTage",
            "allow_channel_1": b"OUTPut1 ON",
            "beep": b"SYSTem:BEEPer:IMMediate"
        }

    def set_frequency(self, frequency):
        self.serial.write(self.settings["set_frequency"] + b" " + str(frequency).encode() + b"\n")

    def beep(self):
        self.serial.write(self.settings["beep"] + b"\n")

    def set_amplitude(self, amplitude):
        self.serial.write(self.settings["set_amplitude"] + b" " + str(amplitude).encode() + b"\n")

    def open_channel(self):
        self.serial.write(self.settings["allow_channel_1"] + b"\n")


class scope:
    def __init__(self):
        self.serial = None
        self.vert_divs = 8
        self.min_voltage_scale = 0.005
        self.max_voltage_scale = 10.0
        self.time_base = [
            1e-9, 2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7,
            1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4,
            1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1,
            1.0, 2.0, 5.0, 10.0, 20.0, 50.0
        ]

    def set_scale(self, frequency, cycles=3):
        T = 1.0 / frequency
        tb_min = (cycles * T) / 10.0
        var = next((tb for tb in self.time_base if tb >= tb_min), self.time_base[-1])
        self.serial.write(f"HORizontal:MAIn:SCAle {var:.6E}")
        atual = self.serial.query("HORizontal:MAIn:SCAle?")
        print("Base atual:", atual)

    def set_voltage_scale_generic(self, ch, target_fill=0.9, tol=0.03, max_iters=5, samples=3):
        s = self.serial
        s.write(f"MEASUrement:IMMed:SOUrce {ch}")
        s.write("MEASUrement:IMMed:TYPe PK2pk")

        def read_vpp_avg(n=samples):
            vals = []
            for _ in range(n):
                try:
                    v = float(s.query("MEASUrement:IMMed:VALue?"))
                    if 0 < v < 9.9e36:
                        vals.append(v)
                except:
                    pass
                time.sleep(0.05)
            return sum(vals)/len(vals) if vals else None

        for _ in range(max_iters):
            vpp = read_vpp_avg()
            if not vpp: return None
            desired = vpp / (target_fill * self.vert_divs)
            desired = max(self.min_voltage_scale, min(desired, self.max_voltage_scale))
            try:
                curr = float(s.query(f"{ch}:SCAle?"))
            except:
                curr = None
            if curr and abs(desired - curr)/curr <= tol:
                return curr
            s.write(f"{ch}:SCAle {desired:.6E}")
            time.sleep(0.15)
        try:
            return float(s.query(f"{ch}:SCAle?"))
        except:
            return None

    def capture_waveform(self, ch="CH2", frequency=None, filename="waveforms.txt", append=True):
        import numpy as np
        import datetime

        s = self.serial
        s.write(f"DATa:SOUrce {ch}")
        s.write("DATa:ENCdg ASCII")
        s.write("DATa:WIDth 1")

        ymult = float(s.query("WFMPRE:YMULT?"))
        yzero = float(s.query("WFMPRE:YZERO?"))
        yoff = float(s.query("WFMPRE:YOFF?"))
        xincr = float(s.query("WFMPRE:XINCR?"))
        xzero = float(s.query("WFMPRE:XZERO?"))

        raw_data = s.query("CURVe?")
        raw_points = np.array([float(p) for p in raw_data.split(",") if p.strip() != ""])

        voltages = (raw_points - yoff) * ymult + yzero
        times = np.arange(len(voltages)) * xincr + xzero

        mode = "a" if append else "w"
        with open(filename, mode) as f:
            f.write(f"# Frequencia: {frequency} Hz ({ch}) - Captura em {datetime.datetime.now()}\n")
            f.write("# Tempo(s),Tensao(V);\n")
            for t, v in zip(times, voltages):
                f.write(f"{t:.9e},{v:.9e};\n")
            f.write("\n")
        print(f"✅ Forma de onda {ch} salva em '{filename}' com {len(voltages)} pontos.")
        return times, voltages

    
class other_serial_device:
    def __init__(self):
        self.serial = None