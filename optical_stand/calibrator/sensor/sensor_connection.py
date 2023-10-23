import serial
from serial.tools.list_ports import comports

device_description: str = 'USB-SERIAL CH340'

def find_comport() -> str | None:
    ports: list = serial.tools.list_ports.comports()
    for name in ports:
        if device_description in name.description:
            return name.device
    return None

if __name__ == "__main__":
    print(find_comport())