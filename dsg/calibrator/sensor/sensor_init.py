import serial
from dsg.calibrator.sensor.sensor_connection import find_comport


class SunSensor():
    "Class representing The Sun and horizon sensor"

    default_baud_rate: int = 1000000
    write_timeout: int = 5
    read_timeout: int = 5
    default_com: str = 'COM4'
    sun_sensor: serial

    def __init__(self) -> None:
        self.sun_sensor: None = None

    def connect(self, com_port = find_comport(), baud_rate = default_baud_rate) -> None:
        self.sun_sensor = serial.Serial(com_port, baud_rate)
        self.sun_sensor.timeout = self.read_timeout
        self.sun_sensor.write_timeout = self.write_timeout

    def write(self, data: bytearray) -> int | None:
        return self.sun_sensor.write(data)

    def read(self, data: int) -> bytes:
        return self.sun_sensor.read(data)

    def flush(self) -> None:
        self.sun_sensor.flushInput()

    def close(self) -> None:
        self.sun_sensor.close()

if __name__ == '__main__':
    ss = SunSensor()
