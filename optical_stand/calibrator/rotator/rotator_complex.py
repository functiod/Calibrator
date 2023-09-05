from dataclasses import dataclass
from optical_stand.calibrator.rotator.rotator_motion import DeviceMotion
from optical_stand.calibrator.rotator.rotator_device import Device
from optical_stand.calibrator.rotator.rotator_settings import Settings
from optical_stand.calibrator.sensor.sensor_processing import Processing


@dataclass
class RotatorControl:
    step_amount: int
    initial_angle: float
    end_angle: float
    azim_steps_count: int = 0
    zen_steps_count: int = 0

class ComplexMotion(Processing, Device, Settings, DeviceMotion):
    "Class for sensor request and pivot rotation"

    def __init__(self) -> None:
        super().__init__()

    def rotate_round_azimuth(self, data: RotatorControl) -> list:
        buff: list = []
        for i in range(data.step_amount):
            self.move_azimuth(self.define_step_angle(data.step_amount, data.initial_angle, data.end_angle, data.azim_steps_count))
            buff.append(self.get_centre_coords())
            data.azim_steps_count += 1
            print('axis 0, axis 1: ', self.get_dev_coord())
            print('///////////////////////////////////')
        self.untangle_wire()
        return buff

    def rotate_round_zenith(self, data: RotatorControl) -> None:
        self.move_zenith(self.define_step_angle(data.step_amount, data.initial_angle, data.end_angle, data.zen_steps_count))
        data.zen_steps_count += 1
        print('axis 0, axis 1: ', self.get_dev_coord())
        print('///////////////////////////////////')

if __name__ == "__main__":
    rotator : ComplexMotion = ComplexMotion()
    rotator.connect_sensor()
    rotator.connect_rotator()
    rotator.initialize_rotator()
    print(rotator.get_dev_coord())
    rotator.set_zen_vel(25.0)
    rotator.set_azim_vel(25.0)
    rotator.set_device_zero_position()
    print(rotator.get_dev_coord())
    v_azim: RotatorControl = RotatorControl(4, 0.0, 360.0)
    v_zen: RotatorControl = RotatorControl(1, 90.0, 150)
    print(rotator.rotate_round_azimuth(v_azim))
    rotator.rotate_round_zenith(v_zen)
