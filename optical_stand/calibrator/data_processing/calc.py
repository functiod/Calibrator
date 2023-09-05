class Calc():
    "Class for math calculation"
    def __init__(self) -> None:
        pass

    def find_coaxial_deviation(self, initialAzimuthAngle: float, initialZenithAngle: float, endAzimuthAngle: float, endZenithAngle: float,
                   numberAzimuthSteps: int, numberZenithSteps: int, fixedAngleRepetition: int) -> np.ndarray:
        self.prepareCalibration(initialAzimuthAngle, initialZenithAngle)
        npbuffer: np.ndarray = self.calibrate(initialAzimuthAngle, initialZenithAngle, endAzimuthAngle, endZenithAngle,
                        numberAzimuthSteps, numberZenithSteps, fixedAngleRepetition)
        deviation_buff: np.ndarray = np.array([self.__find_matrix_dispersion(npbuffer, self.radiusSensCol,
                                                x*numberAzimuthSteps, (x+1)*numberAzimuthSteps) for x in range(numberZenithSteps + 1)])
        temp_list: list = [0] * (numberAzimuthSteps - 1) * (numberZenithSteps + 1) * fixedAngleRepetition
        for i, value in enumerate(deviation_buff):
            temp_list.insert((i+1) * numberAzimuthSteps - 1, value)
        result_list: np.ndarray = np.array([npbuffer[:, self.zenRotatorCol], temp_list[:]])
        self.TotNumAzimSteps = 0
        self.TotNumZenSteps = 0
        return result_list

    def __find_matrix_dispersion(self, buffer: list, col: int, start: int, end: int) -> float:
        column: list = [row[col] for row in buffer]
        column_slice: list = column[start:end]
        return moment(column_slice, self.dispersion)

    def find_least_dev(self) -> float:
        files: list = os.listdir(self.Normal_fall_folder)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(self.Normal_fall_folder, x)))
        last_file: str = files[-1]
        dev_matrix: list = self.downloadFile(f"{self.Normal_fall_folder}/{last_file}")
        dev_dict: dict = {key: value for key, value in dev_matrix if value != 0.0}
        min_value: float = min(dev_dict.values())
        key_for_min_value: float = float(next((key for key, value in dev_dict.items() if value == min_value), None))
        return key_for_min_value

    def defineAproxPolynom(self, buffer: list)-> list:
        npbuffer: np.ndarray = np.array(buffer)
        radius: list = npbuffer[:, self.radiusSensCol]
        thetta: list = npbuffer[:, self.zenRotatorCol]
        A: list = np.vstack([radius**i for i in range(self.order_of_polynom + 1)]).T
        coefficients: list = lsq_linear(A, thetta).x
        return coefficients

    def defineZenithDeviation(self, buffer: list) -> tuple:
        npbuffer: np.ndarray = np.array(buffer)
        coefs: list = self.defineAproxPolynom(npbuffer)
        polynomial = np.poly1d(np.flip(coefs))
        deviationBuff: list = polynomial(npbuffer[:, self.radiusSensCol]) - npbuffer[:, self.zenRotatorCol]
        angleBuff: list = npbuffer[:, self.zenRotatorCol]
        return (angleBuff, deviationBuff)