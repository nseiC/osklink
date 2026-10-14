import pyvisa
import usbtmc_fix
import serial.tools.list_ports 
import time
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox

usbtmc_fix.apply()


def list_serial_ports():
    """Portas seriais reais. No Linux o comports() também lista /dev/ttyS0..31,
    que são portas legadas que não existem fisicamente (hwid 'n/a')."""
    return [p.device for p in serial.tools.list_ports.comports() if p.hwid != "n/a"]


def usbtmc_clear(resource_name):
    """Destrava um instrumento USBTMC que ficou com uma resposta pendente
    (ex.: o app foi fechado no meio de um CURVe?). Sem isso o osciloscópio passa a
    recusar qualquer comando com timeout até ser desligado. O clear() do pyvisa-py
    não é suportado em USB, então os pedidos USBTMC são feitos direto via pyusb."""
    if not resource_name.startswith("USB"):
        return
    try:
        import usb.core
        import usb.util
        _, vid, pid, serial_number = resource_name.split("::")[:4]
        dev = usb.core.find(idVendor=int(vid, 0), idProduct=int(pid, 0),
                            custom_match=lambda d: d.serial_number == serial_number)
        if dev is None:
            return
        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)
        usb.util.claim_interface(dev, 0)
        intf = dev.get_active_configuration()[(0, 0)]
        # INITIATE_CLEAR / CHECK_CLEAR_STATUS (USBTMC 1.0, seção 4.2.1.6 e 4.2.1.7)
        dev.ctrl_transfer(0xA1, 5, 0, 0, 1, timeout=2000)
        for _ in range(20):
            if dev.ctrl_transfer(0xA1, 6, 0, 0, 2, timeout=2000)[0] != 2:
                break
            time.sleep(0.1)
        for ep in intf:
            if usb.util.endpoint_type(ep.bmAttributes) == usb.util.ENDPOINT_TYPE_BULK:
                dev.clear_halt(ep.bEndpointAddress)
        usb.util.release_interface(dev, 0)
        usb.util.dispose_resources(dev)
    except Exception as e:
        print("Aviso: não foi possível limpar o USBTMC:", e)


def set_usb_write_timeout(resource, timeout_ms):
    """O pyvisa-py 0.7 ignora o timeout do VISA nas escritas USB e usa o padrão do
    pyusb (1 s). O TBS demora mais que isso para aceitar comandos enquanto prepara o
    CURVe?, e o timeout deixa o osciloscópio travado. Ajusta o timeout no pyusb."""
    try:
        session = resource.visalib.sessions[resource.session]
        session.interface.usb_dev.default_timeout = timeout_ms
    except (AttributeError, KeyError):
        pass  # outro backend VISA (NI-VISA, TekVISA) ou recurso não USB


def list_visa_resources(rm):
    """Recursos VISA sem as portas seriais fantasmas, com os USB (osciloscópio) primeiro."""
    real_ports = set(list_serial_ports())
    resources = []
    for res in rm.list_resources():
        if res.startswith("ASRL"):
            device = res[len("ASRL"):].split("::")[0]
            if device not in real_ports:
                continue
        resources.append(res)
    return sorted(resources, key=lambda r: not r.startswith("USB"))

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
        scope_name = self.scope_options.mybtn.currentText()
        usbtmc_clear(scope_name)
        self.myscope = self.rm.open_resource(scope_name)
        # O padrão do pyvisa é 2 s, curto demais para o CURVe? do TBS via pyvisa-py
        self.myscope.timeout = 10000
        set_usb_write_timeout(self.myscope, 10000)
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
            for res in list_visa_resources(self.rm):
                self.mybtn.addItem(res)
        elif mystr == 'Gerador de funções':
            for p in list_serial_ports():
                self.mybtn.addItem(p)
        elif mystr == 'Outro dispositivo serial':
            for p in list_serial_ports():
                self.mybtn.addItem(p)
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
        # Binário (1 byte com sinal por ponto) é ~4x menor e bem mais rápido que ASCII
        s.write("DATa:ENCdg RIBinary")
        s.write("DATa:WIDth 1")

        ymult = float(s.query("WFMPRE:YMULT?"))
        yzero = float(s.query("WFMPRE:YZERO?"))
        yoff = float(s.query("WFMPRE:YOFF?"))
        xincr = float(s.query("WFMPRE:XINCR?"))
        xzero = float(s.query("WFMPRE:XZERO?"))

        raw_points = s.query_binary_values("CURVe?", datatype="b", container=np.array).astype(float)

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