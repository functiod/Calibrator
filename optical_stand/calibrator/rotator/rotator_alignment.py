class Alignment():
    "Class for the rotator adjustment"
    def __init__(self) -> None:
        pass

    def alignCenter(self, file_calib: str) -> list:
        mybuffer: list = self.downloadFile(file_calib)
        npbuffer: np.ndarray = np.array(mybuffer)
        npbuffer[:, self.zenRotatorCol] = npbuffer[:, self.zenRotatorCol] - self.find_least_dev()
        npbuffer[:, self.radiusSensCol] = np.sqrt((npbuffer[:, self.xSensCol] - self.find_coax_x_y(file_calib, self.find_least_dev())[self.xSensCol])**2 +
                                                   (npbuffer[:, self.ySensCol] - self.find_coax_x_y(file_calib, self.find_least_dev())[self.ySensCol])**2)
        return npbuffer

    def find_coax_x_y(self, filename: str, center_value_key: float) -> tuple:
        calib_buff: np.ndarray = np.array(self.downloadFile(filename))
        buff_of_dicts: list = [{calib_buff[i][self.zenRotatorCol]:(calib_buff[i][self.xSensCol], calib_buff[i][self.ySensCol])}
                                for i in range(len(calib_buff[:, self.xSensCol]))]
        def_dict = defaultdict(list)
        for mydict in buff_of_dicts:
            for key, value in mydict.items():
                def_dict[key].append(value)
        x_centre: float = np.average(np.array(def_dict[center_value_key])[:, self.xSensCol])
        y_centre: float = np.average(np.array(def_dict[center_value_key])[:, self.ySensCol])
        return x_centre, y_centre