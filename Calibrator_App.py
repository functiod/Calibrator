from os import listdir
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtCore import QSettings
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from calibrationSensor import Calibrator
import design

class MainWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.calibrator = Calibrator()
        self.init_Button.clicked.connect(self.connect)
        self.disable_Button.clicked.connect(self.disconnect)

        self.settings_widgets: dict = {}
        for i in range(self.settings_layout.count()):
            self.settings_widgets[i] = self.settings_layout.itemAt(i).widget()

        self.save_settings_Button.clicked.connect(self.save_settings)
        self.set_zero_Button.clicked.connect(self.to_zero_position)
        self.calibration_Button.clicked.connect(self.main_programm)

    def connect(self) -> None:
        self.calibrator.initialize()

    def disconnect(self) -> None:
        self.calibrator.disable()

    def save_settings(self) -> None:
        for _, widget in self.settings_widgets.items():
            value: float = widget.value()
            varible_temp_name: str = widget.objectName()
            slice_index: str = varible_temp_name.find('_Button')
            varible_name: str = varible_temp_name[:slice_index]
            setattr(self, varible_name, value)

    def to_zero_position(self) -> None:
        self.calibrator.setDevZeroPosition(self.init_zen_sett)

    # def main_programm(self) -> None:
    #     self.calibrator.prepareBuffer(self.num_azim_steps_sett, self.num_zen_steps_sett, self.fixed_angle_rep_sett)
    #     self.calibrator.prepareCalibration(self.init_azim_sett, self.init_zen_sett)
    #     self.calibrator.Calibrate(self.init_azim_sett, self.init_zen_sett, self.end_azim_sett,
    #                                self.end_zen_sett, self.num_azim_steps_sett, self.num_zen_steps_sett,
    #                                self.zen_vel_sett, self.azim_vel_sett, self.fixed_angle_rep_sett)
    #     self.calibrator.saveToFile(self.calibrator.getBuffer())

    def main_programm(self) -> None:
        self.calibrator.prepareBuffer(self.num_azim_steps_sett, self.num_zen_steps_sett, self.fixed_angle_rep_sett)
        self.calibrator.prepareCalibration(self.init_azim_sett, self.init_zen_sett)
        self.calibrator.Calibrate(self.init_azim_sett, self.init_zen_sett, self.end_azim_sett,
                                   self.end_zen_sett, self.num_azim_steps_sett, self.num_zen_steps_sett,
                                   self.zen_vel_sett, self.azim_vel_sett, self.fixed_angle_rep_sett)
        self.calibrator.saveToFile(self.calibrator.getBuffer())
        self.calibrator.prepareCalibration(0, 272.5)

    # def choose_file(self) -> None:
    #     for file in listdir('IntensityTables'):
    #         self.calibration_files_widget.addItem(file)
    #     self.calibration_files_widget.setSelectionMode(QAbstractItemView.SingleSelection)

def main() -> None:
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
