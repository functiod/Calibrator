from dsg.calibrator.rotator.rotator_pivot import Pivot
from dsg.calibrator.rotator.rotator_pivot import Axis


class Device:
    "Class represnting rotator's properties"

    def __init__(self) -> None:
        self.device_zenith: Pivot = Pivot(Axis.zenith)
        self.device_azimuth: Pivot = Pivot(Axis.azimuth)

    def connect_rotator(self) -> None:
        self.device_azimuth.connect_TCP()
        self.device_zenith.connect_TCP()

    def initialize_rotator(self) -> None:
        self.device_azimuth.initialize()
        self.device_zenith.initialize()

    def disable_rotator(self) -> None:
        self.device_azimuth.disable()
        self.device_zenith.disable()

    def get_coord_zen(self) -> float:
        return self.device_zenith.get_coord()

    def get_coord_azim(self) -> float:
        return self.device_azimuth.get_coord()

if __name__ == "__main__":
    device: Device = Device()
    device.connect_rotator()
    device.initialize_rotator()
    device.disable_rotator()
