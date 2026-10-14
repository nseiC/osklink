# OscLink
Create a interface to DSO2D15. 

## Rodando no Linux

Dependências do sistema (Ubuntu/Debian):

```bash
sudo apt install python3-pyqt5 python3-numpy python3-pandas python3-serial python3-pyvisa python3-pyvisa-py python3-usb libportaudio2
pip install sounddevice
```

Ou, num ambiente virtual: `pip install -r requirements.txt` (ainda é preciso o `libportaudio2` do apt para o áudio).

Permissões para acessar o osciloscópio Tektronix (USBTMC) e o gerador (CH340, `/dev/ttyUSB*`):

```bash
sudo cp udev/99-osclink.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Depois disso, desconecte e reconecte os cabos USB. Não é preciso instalar TekVISA nem NI-VISA (o TekVISA só existe
para Windows): o `pyvisa-py` fala direto com o osciloscópio via USB.

Executar:

```bash
python3 main.py
```

### VS Code instalado via snap

O VS Code em snap injeta variáveis de ambiente (`GTK_PATH`, `GIO_MODULE_DIR`, ...) que fazem o Qt carregar
bibliotecas do snap `core20` e quebram com `symbol lookup error: ... libpthread.so.0: undefined symbol: __libc_pthread_init`.
O `linux_env.py` limpa essas variáveis automaticamente na inicialização do `main.py`.
O aviso `QSocketNotifier: Can only be used with threads started with QThread` vem do depurador do VS Code e pode ser ignorado.
