from optical_stand.calibrator.rotator.rotator_pivot import Pivot
from optical_stand.calibrator.rotator.rotator_pivot import Axis


class DeviceMotion:
    "Class for Device motion controll"

    def __init__(self) -> None:
        pass

    def set_device_zero_position(self) -> None:
        Pivot(Axis.zenith).set_zero_position()

    def set_azim_init_pos(self, init_angle: float) -> None:
        Pivot(Axis.azimuth).absolute_rotation(init_angle)

    def set_zen_init_pos(self, init_angle: float) -> None:
        Pivot(Axis.zenith).absolute_rotation(init_angle)

    def move_azimuth(self, step_angle: float) -> None:
        Pivot(Axis.zenith).absolute_rotation(step_angle)

    def move_zenith(self, step_angle: float) -> None:
        Pivot(Axis.zenith).absolute_rotation(step_angle)

    def untangle_wire(self) -> None:
        Pivot(Axis.azimuth).absolute_rotation(Pivot.MIN_COORD)
