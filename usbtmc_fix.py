"""Correção da leitura USBTMC do pyvisa-py para o Tektronix TBS 1102B no Linux.

O TBS declara endpoints bulk de 64 bytes numa conexão USB high-speed (o padrão
exige 512; o kernel avisa "bulk endpoint ... has invalid maxpacket 64"). Nos
controladores xHCI cada pacote de 64 bytes encerra a leitura, então uma resposta
maior que 52 bytes (64 - 12 de cabeçalho) chega picotada em vários pedaços.

O pyvisa-py lê só o primeiro pedaço e já envia o próximo REQUEST_DEV_DEP_MSG_IN;
o osciloscópio, que ainda tem o resto da resposta para entregar, recusa o pedido
e a comunicação trava com timeout (WFMPre?, CURVe?, ...). No Windows o driver
junta os pedaços e o problema não aparece.

Aqui a leitura continua até receber todos os bytes anunciados no cabeçalho.
"""

try:
    import usb.core
    from pyvisa_py.protocols import usbtmc as _usbtmc
except ImportError:  # outro backend VISA (NI-VISA, TekVISA no Windows)
    _usbtmc = None

HEADER_SIZE = 12
MAX_TRANSFER = 1 << 16


def _read(self, size):
    recv_chunk = size if 0 < size < MAX_TRANSFER else MAX_TRANSFER
    raw_read = super(_usbtmc.USBTMC, self).read
    raw_write = super(_usbtmc.USBTMC, self).write

    received = bytearray()
    eom = False
    while not eom:
        self._btag = (self._btag % 255) + 1
        raw_write(_usbtmc.BulkInMessage.build_array(self._btag, recv_chunk, None))

        try:
            response = _usbtmc.BulkInMessage.from_bytes(raw_read(recv_chunk + HEADER_SIZE + 3))
            data = bytearray(response.data)
            # Busca o resto da transferência que chegou picotada
            while len(data) < response.transfer_size:
                data += raw_read(response.transfer_size - len(data) + 3)
        except (usb.core.USBError, ValueError):
            self._abort_bulk_in(self._btag)
            raise

        received.extend(data[:response.transfer_size])
        eom = response.transfer_attributes & 1

    return bytes(received)


def apply():
    if _usbtmc is not None:
        _usbtmc.USBTMC.read = _read
