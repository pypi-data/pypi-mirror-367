import struct

import serial

from ecowitt_wn90lp.ws90 import WS90DataRate


def modbus_crc(msg: bytes) -> int:
    crc = 0xFFFF
    for n in msg:
        crc ^= n
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


if __name__ == "__main__":
    dev = serial.Serial('/dev/ttyUSB0', baudrate=9600)

    msg = b'\xFD\xFD\xFD\x00\x00'
    crc = struct.pack('<H', modbus_crc(msg))
    dev.write(msg + crc)

    reply = dev.read(7)

    print(f"Baud Rate: {WS90DataRate(reply[3]).rate}")
    print(f"Address: 0x{reply[4].to_bytes().hex():2}")


