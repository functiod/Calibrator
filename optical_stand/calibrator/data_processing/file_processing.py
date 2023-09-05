class FileProcessing():
    "Class for ease of working with files"
    def __init__(self) -> None:
        pass

    def convertDataFormCSV(self, data: tuple) -> tuple:
        '''Converts exponential to float with four digits for CSV and TXT files'''
        return tuple([round(float(x), 4) for x in data])

    def save_dev_to_file(self, buffer: list) -> None:
        rot_zen_angle_col: int = 0
        dist_dev_col: int = 1
        npbuffer: np.ndarray = np.array(buffer)
        data: dict = {
            'Rotator_Zenith_angle' : npbuffer[rot_zen_angle_col, :],
            'Radius_deviation': npbuffer[dist_dev_col, :]
        }
        to_file: str = datetime.now().strftime(f"{self.Normal_fall_folder}\\%m-%d-%Y_%H-%M-%S_Normal_fall.csv")
        df = pd.DataFrame(data)
        df.to_csv(to_file, index = False, header = False, sep = ' ', na_rep = 'nan')

    def saveToFileCSV(self, buffer: list | None = None, from_file: str = '') -> None:
        if from_file != '':
            mybuffer: list = self.downloadFile(from_file)
        else:
            mybuffer: list = buffer if buffer.any() else self.imageBuffer
        npbuffer: np.ndarray = np.array(mybuffer)
        data: dict = {
            'x_sensity' : npbuffer[:, self.xSensCol],
            'y_sensity' : npbuffer[:, self.ySensCol],
            'zenith_sensity' : npbuffer[:, self.zenSensCol],
            'azimuth_sensity' : npbuffer[:, self.azimSensCol],
            'Rotator_Zenith_angle' : npbuffer[:, self.zenRotatorCol],
            'Rotator_Azimuth_angle' : npbuffer[:, self.azimRotatorCol],
            'Radius' : npbuffer[:, self.radiusSensCol]
        }
        to_file: str = datetime.now().strftime(f"{self.calibFolder}\\%m-%d-%Y_%H-%M-%S_Intensity.csv")
        df = pd.DataFrame(data)
        df.to_csv(to_file, index = False, header = False, sep = ' ', na_rep = 'nan')
        return to_file

    def downloadFile(self, filename: str) -> list:
        calibMatrix: list = []
        with open(filename, 'r+', encoding = 'utf-8') as file:
            for _, line in enumerate(file):
                calibMatrix.append([float(str_num) for str_num in line.split()])
        return calibMatrix

    def saveToXLSX(self, from_file: str = '') -> None:
        if from_file != '':
            mybuffer: list = self.downloadFile(from_file)
        else:
            mybuffer: list = self.imageBuffer
        npbuffer: np.ndarray = np.array(mybuffer)
        to_file: str = datetime.now().strftime(f"{self.calibFolder}\\%m-%d-%Y_%H-%M-%S_Intensity.xlsx")
        wb = openpyxl.Workbook()
        ws = wb.active
        for row in npbuffer:
            ws['A1:A{}'.format(len(row))][0][0].number_format = '0.0000'
            ws.append(list(row))
        wb.save(to_file)

    # def convertDataFormCSV(self, data: tuple) -> tuple:
    #     '''Converts exponential to float with four digits for CSV and TXT files'''
    #     return tuple([round(float(x), 4) for x in data])