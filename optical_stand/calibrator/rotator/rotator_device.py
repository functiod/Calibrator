from optical_stand.calibrator.rotator.rotator_pivot import Pivot
from optical_stand.calibrator.rotator.rotator_pivot import Axis


class Device:
    "Class represnting rotator's properties"

    def __init__(self) -> None:
        pass

    def connect_rotator(self) -> None:
        Pivot(Axis.zenith).connect_TCP()

    def initialize_rotator(self) -> None:
        Pivot(Axis.azimuth).initialize()
        Pivot(Axis.zenith).initialize()

    def disable_rotator(self) -> None:
        Pivot(Axis.azimuth).disable()
        Pivot(Axis.zenith).disable()

if __name__ == "__main__":
    device: Device = Device()
    device.connect_rotator()
    device.initialize_device(0)
    device.disable_device(0)