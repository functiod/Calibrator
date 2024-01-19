from dataclasses import dataclass
from dsg.calibrator.rotator.rotator_motion import DeviceMotion
from dsg.calibrator.rotator.rotator_settings import Settings
from dsg.calibrator.sensor.sensor_processing import Processing
from dsg.calibrator.data_processing.file_processing import save_calib_to_csv
from dsg.calibrator.data_processing.file_processing import save_log_to_csv
from dsg.calibrator.data_processing.after_processing import adjust_calib_data
from dsg.calibrator.data_processing.rotator_alignment import find_zenith_coax
import numpy as np
import pandas as pd
import time
import threading


@dataclass
class RotatorControl:
    step_amount: int
    initial_angle: float
    end_angle: float
    azim_steps_count: int = 0
    zen_steps_count: int = 0

class ComplexMotion(DeviceMotion, Settings, Processing):
    "Class for sensor request and pivot rotation"
    x_sens: int = 0
    y_sens: int = 1
    zen_sens: int = 2
    azim_sens: int = 3
    EPS: float = 0.001

    def __rotate_round_azimuth(self, data: RotatorControl) -> np.ndarray:
        'Returns matrix of measured intensities at current angle from solar imitator'
        image_buff: list = []
        for i in range(data.step_amount):
            if data.azim_steps_count % data.step_amount == 0:
                end_angle: float = 0.0
            else:
                end_angle = data.end_angle
            self.move_azimuth(self.define_step_angle(data.step_amount, data.initial_angle, end_angle, data.azim_steps_count))
            time.sleep(1)
            image_buff.append([*self.get_centre_coords(), *self.get_dev_coord()])
            data.azim_steps_count += 1
        self.untangle_wire()
        return np.array(image_buff)

    def __rotate_round_zenith(self, data: RotatorControl) -> None:
        data.zen_steps_count += 1
        self.move_zenith(self.define_step_angle(data.step_amount, data.initial_angle, data.end_angle, data.zen_steps_count))

    def align_collect_data(self, data_zen: RotatorControl, data_azim: RotatorControl) -> np.ndarray:
        self.move_zenith(data_zen.initial_angle)
        final_buffer: list = []
        for i in range(data_zen.step_amount):
            image_buff: np.ndarray = self.__rotate_round_azimuth(data_azim)
            if i == 0:
                final_buffer = image_buff
            else:
                final_buffer = np.concatenate((final_buffer, image_buff))
            self.__rotate_round_zenith(data_zen)
        final_buffer: np.ndarray = np.array(final_buffer)
        save_calib_to_csv(final_buffer, folder_path=r'utils/Normal_fall')
        return final_buffer

    def rotate_collect_data(self, data_zen: RotatorControl, data_azim: RotatorControl, df_normal: pd.DataFrame) -> np.ndarray:
        coax_zenith: float = find_zenith_coax(df_normal)
        self.move_zenith(coax_zenith)
        final_buffer: list = []
        for i in range(data_zen.step_amount):
            image_buff: np.ndarray = adjust_calib_data(self.__rotate_round_azimuth(data_azim), df_normal)
            if i == 0:
                final_buffer = image_buff
            else:
                final_buffer = np.concatenate((final_buffer, image_buff))
            self.__rotate_round_zenith(data_zen)
        final_buffer: np.ndarray = np.array(final_buffer)
        save_calib_to_csv(final_buffer, folder_path=r'utils/Intensity_tables')
        return final_buffer

    def rotate_angle_velocity(self, velocity: float, data_zen: RotatorControl) -> None:
        initial_time: float = time.time()
        self.set_zen_vel(velocity)
        sensor_coord: float = self.get_centre_coords()[self.zen_sens]
        current_time: float = time.time()
        rotator_coord: float = self.get_coord_zen()
        log_buffer: list = []
        log_buffer.append([sensor_coord, rotator_coord, current_time, initial_time])
        while abs(self.get_coord_zen() - data_zen.end_angle) >= self.EPS:
            sensor_coord: float = self.get_centre_coords()[self.zen_sens]
            current_time: float = time.time()
            rotator_coord: float = self.get_coord_zen()
            log_buffer.append([sensor_coord, rotator_coord, current_time, initial_time])
        log_buffer = np.array(log_buffer)
        save_log_to_csv(log_buffer)

    def async_vel_request(self, velocity, data_zen: RotatorControl) -> None:
        self.set_zen_vel(velocity)
        t_1 = threading.Thread(target=self.move_zenith, args=(data_zen.end_angle,))
        t_2 = threading.Thread(target=self.rotate_angle_velocity, args=(velocity, data_zen,))
        t_1.start()
        t_2.start()
        t_1.join()
        t_2.join()

if __name__ == "__main__":
    rotator: ComplexMotion = ComplexMotion()
    rotator.connect_rotator()
    rotator.initialize_rotator()
    rotator.set_zen_vel(50.0)
    rotator.set_azim_vel(50.0)
    rotator.set_device_zero_position()
    rotator.connect()
    data_vector_azim: RotatorControl = RotatorControl(4, 0.0, 360.0)
    data_vector_zen: RotatorControl = RotatorControl(5, 213.0, 333.0)
    rotator.move_zenith(data_vector_zen.initial_angle)
    for i in range(1, 30):
        if i % 2 != 0:
            data_vector_zen: RotatorControl = RotatorControl(5, 213.0, 333.0)
        else:
            data_vector_zen: RotatorControl = RotatorControl(5, 333.0, 213.0)
        rotator.async_vel_request(i, data_vector_zen)
    # rotator.rotate_angle_velocity(10, data_vector_zen)
    # rotator.align_collect_data(data_vector_zen, data_vector_azim)
    # rotator.rotate_collect_data(data_vector_zen, data_vector_azim, r'D:\python_projects\Calibrator\utils\Normal_fall\01-12-2024_16-03-53_Intensity.csv')
    # rotator.disable_rotator()
