from dataclasses import dataclass
from optical_stand.calibrator.rotator.rotator_motion import DeviceMotion
from optical_stand.calibrator.rotator.rotator_settings import Settings
from optical_stand.calibrator.sensor.sensor_processing import Processing
from optical_stand.calibrator.data_processing.file_processing import save_calib_to_csv
from optical_stand.calibrator.data_processing.after_processing import adjust_calib_data
import numpy as np
import pandas as pd


@dataclass
class RotatorControl:
    step_amount: int
    initial_angle: float
    end_angle: float
    azim_steps_count: int = 0
    zen_steps_count: int = 0

class ComplexMotion(DeviceMotion, Settings, Processing):
    "Class for sensor request and pivot rotation"

    def __rotate_round_azimuth(self, data: RotatorControl) -> np.ndarray:
        'Returns matrix of measured intensities at current angle from solar imitator'
        image_buff: np.ndarray = np.array([])
        for i in range(data.step_amount):
            self.move_azimuth(self.define_step_angle(data.step_amount, data.initial_angle, data.end_angle, data.azim_steps_count))
            np.append(image_buff, [*self.get_centre_coords(), self.get_dev_coord])
            data.azim_steps_count += 1
        self.untangle_wire()
        return image_buff

    def __rotate_round_zenith(self, data: RotatorControl) -> None:
        data.zen_steps_count += 1
        self.move_zenith(self.define_step_angle(data.step_amount, data.initial_angle, data.end_angle, data.zen_steps_count))

    def align_collect_data(self, data_zen: RotatorControl, data_azim: RotatorControl) -> np.ndarray:
        self.move_zenith(data_zen.initial_angle)
        final_buffer: np.ndarray = np.array([])
        for i in range(data_zen.step_amount):
            np.append(final_buffer, self.__rotate_round_azimuth(data_azim))
            self.__rotate_round_zenith(data_zen)
        save_calib_to_csv(final_buffer, folder_path='utils\Normal_fall')
        return final_buffer

    def rotate_collect_data(self, data_zen: RotatorControl, data_azim: RotatorControl, df_normal: pd.DataFrame) -> np.ndarray:
        self.move_zenith(data_zen.initial_angle)
        final_buffer: np.ndarray = np.array([])
        for i in range(data_zen.step_amount):
            image_buff: np.ndarray = adjust_calib_data(self.__rotate_round_azimuth(data_azim), df_normal)
            np.append(final_buffer, image_buff)
            self.__rotate_round_zenith(data_zen)
        save_calib_to_csv(final_buffer, folder_path='utils\Intensity_tables')
        return final_buffer

if __name__ == "__main__":
    rotator: ComplexMotion = ComplexMotion()
    rotator.connect_rotator()
    rotator.initialize_rotator()
    rotator.set_zen_vel(25.0)
    rotator.set_azim_vel(25.0)
    rotator.move_azimuth(0.0)
    # rotator.set_device_zero_position()
    rotator.connect_sensor()
    data_vector_azim: RotatorControl = RotatorControl(4, 0.0, 360.0)
    data_vector_zen: RotatorControl = RotatorControl(1, 90.0, 180.0)
    print(rotator.rotate_round_azimuth(data_vector_azim))
    rotator.rotate_round_zenith(data_vector_zen)
    rotator.disable_rotator()
