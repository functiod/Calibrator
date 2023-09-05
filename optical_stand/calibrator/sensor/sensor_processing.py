from optical_stand.calibrator.sensor.sensor_tools import Tools


class Processing():
    "Additional Sensor tools"

    def __init__(self) -> None:
        self.tools: Tools = Tools()

    def connect_sensor(self) -> None:
        self.tools.sensor.connect()

    def set_settings(self) -> None:
        self.tools._setGamsettings()
        self.tools._settingsMatrix()

    def get_centre_coords(self) -> tuple[float, float, float, float]:
        self.set_settings()
        image: tuple[float, float, float, float] = self.tools.getImg10bit()
        return image

if __name__ == "__main__":
    proc: Processing = Processing()
    proc.connect_device()
    print(proc.get_centre_coords())
