from dsg.calibrator.data_processing.file_processing import FileProcessing
from dsg.calibrator.data_processing.calc import Calc
import numpy as np
import pandas as pd

class Alignment(FileProcessing, Calc):
    "Class for the rotator adjustment"

    def alignCenter(self, file_calib: str) -> pd.DataFrame:
        calib_df: pd.DataFrame = self.read_calib_from_csv(file_calib)
        calib_df['zenith angle'] = calib_df['zenith angle'] - self.find_least_dev()
        radius_data: np.ndarray = np.sqrt((calib_df['x sens'] - self.find_coax_x_y(file_calib, self.find_least_dev())[self.xSensCol])**2 +
                                                   (calib_df['y sens'] - self.find_coax_x_y(file_calib, self.find_least_dev())[self.ySensCol])**2)
        radius_df = pd.DataFrame({'radius sens' : radius_data})
        calib_df.join(radius_df)
        return calib_df

    def find_coax_x_y(self, filename: str, center_value_key: float) -> tuple:
        calib_buff: np.ndarray = np.array(self.download_file(filename))
        buff_of_dicts: list = [{calib_buff[i][self.zenRotatorCol]:(calib_buff[i][self.xSensCol], calib_buff[i][self.ySensCol])}
                                for i in range(len(calib_buff[:, self.xSensCol]))]
        def_dict = defaultdict(list)
        for mydict in buff_of_dicts:
            for key, value in mydict.items():
                def_dict[key].append(value)
        x_centre: float = np.average(np.array(def_dict[center_value_key])[:, self.xSensCol])
        y_centre: float = np.average(np.array(def_dict[center_value_key])[:, self.ySensCol])
        return x_centre, y_centre