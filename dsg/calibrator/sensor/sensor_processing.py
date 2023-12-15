from dsg.calibrator.sensor.sensor_tools import Tools


class Processing(Tools):
    "Additional Sensor tools"

    def connect_sensor(self) -> None:
        self.connect()

    def set_settings(self) -> None:
        self._setGamsettings()
        self._settingsMatrix()

    def get_centre_coords(self) -> tuple[float, float, float, float]:
        self.set_settings()
        while True:
            try:
                image: tuple[float, float, float, float] = self.getImg10bit()
                if isinstance(image, tuple):
                    break
            except UnboundLocalError:
                image: tuple[float, float, float, float] = self.getImg10bit()
                if isinstance(image, tuple):
                    break
        image_list: list[float, float, float, float] = [round(float(image[i]), 4) for i in range(len(image))]
        return image_list

if __name__ == "__main__":
    proc: Processing = Processing()
    proc.connect_sensor()
    print(proc.get_centre_coords())
