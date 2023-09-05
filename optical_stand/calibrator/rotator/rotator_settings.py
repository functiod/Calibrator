from optical_stand.calibrator.rotator.rotator_pivot import Pivot
from optical_stand.calibrator.rotator.rotator_pivot import Axis


class Settings():
    "Class for set up the motion settings"

    def __init__(self) -> None:
        pass

    def set_azim_vel(self, velocity: float) -> None:
        Pivot(Axis.azimuth).set_velocity(velocity)

    def set_zen_vel(self, velocity: float) -> None:
        Pivot(Axis.zenith).set_velocity(velocity)

    def set_azim_acc(self, acceleration: float) -> None:
        Pivot(Axis.azimuth).set_acceleration(acceleration)

    def set_zen_acc(self, acceleration: float) -> None:
        Pivot(Axis.zenith).set_acceleration(acceleration)

    def get_dev_coord(self) -> tuple[float, float]:
        azim_coord: float = Pivot(Axis.azimuth).get_coord()
        zen_coord: float = Pivot(Axis.zenith).get_coord()
        return zen_coord, azim_coord

    def define_step_angle(self, step_amount: int, initial_angle: float, end_angle: float, step_number: int) -> float:
       if step_number % step_amount == 0 and step_number != 0:
           angle: float = end_angle
       else:
           angle: float = initial_angle + (end_angle - initial_angle) * (step_number % step_amount) / step_amount
       return angle
