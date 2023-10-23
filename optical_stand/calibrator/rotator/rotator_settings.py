from optical_stand.calibrator.rotator.rotator_device import Device


class Settings(Device):
    "Class for set up the motion settings"

    def set_azim_vel(self, velocity: float) -> None:
        self.device_azimuth.set_velocity(velocity)

    def set_zen_vel(self, velocity: float) -> None:
        self.device_zenith.set_velocity(velocity)

    def set_azim_acc(self, acceleration: float) -> None:
        self.device_azimuth.set_acceleration(acceleration)

    def set_zen_acc(self, acceleration: float) -> None:
        self.device_zenith.set_acceleration(acceleration)

    def get_dev_coord(self) -> tuple[float, float]:
        azim_coord: float = round(float(self.device_azimuth.get_coord(), 3))
        zen_coord: float = round(float(self.device_zenith.get_coord(), 3))
        return zen_coord, azim_coord

    def define_step_angle(self, step_amount: int, initial_angle: float, end_angle: float, step_number: int) -> float:
       if step_number % step_amount == 0 and step_number != 0:
           angle: float = end_angle
       else:
           angle: float = initial_angle + (end_angle - initial_angle) * (step_number % step_amount) / step_amount
       return angle
