from dsg.calibrator.rotator.rotator_device import Device
from dsg.calibrator.rotator.rotator_pivot import Pivot


class DeviceMotion(Device):
    "Class for Device motion controll"

    def set_device_zero_position(self) -> None:
        'Used only for zenith because there is no zero pos. for azimuth'
        self.device_zenith.set_zero_position()

    def set_azim_init_pos(self, init_angle: float) -> None:
        self.device_azimuth.absolute_rotation(init_angle)

    def set_zen_init_pos(self, init_angle: float) -> None:
        self.device_zenith.absolute_rotation(init_angle)

    def move_azimuth(self, to_angle: float) -> None:
        self.device_azimuth.absolute_rotation(to_angle)

    def move_zenith(self, to_angle: float) -> None:
        self.device_zenith.absolute_rotation(to_angle)

    def untangle_wire(self) -> None:
        self.device_azimuth.absolute_rotation(Pivot.MIN_COORD)
