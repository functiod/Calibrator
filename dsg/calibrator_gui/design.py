# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1521, 859)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 121, 371))
        self.layoutWidget.setObjectName("layoutWidget")
        self.action_layout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.action_layout.setContentsMargins(0, 0, 0, 0)
        self.action_layout.setObjectName("action_layout")
        self.init_Button = QtWidgets.QPushButton(self.layoutWidget)
        self.init_Button.setCheckable(True)
        self.init_Button.setChecked(False)
        self.init_Button.setObjectName("init_Button")
        self.action_layout.addWidget(self.init_Button)
        self.set_zero_Button = QtWidgets.QPushButton(self.layoutWidget)
        self.set_zero_Button.setObjectName("set_zero_Button")
        self.action_layout.addWidget(self.set_zero_Button)
        self.single_start_Button = QtWidgets.QPushButton(self.layoutWidget)
        self.single_start_Button.setObjectName("single_start_Button")
        self.action_layout.addWidget(self.single_start_Button)
        self.disable_Button = QtWidgets.QPushButton(self.layoutWidget)
        self.disable_Button.setObjectName("disable_Button")
        self.action_layout.addWidget(self.disable_Button)
        self.calibration_Button = QtWidgets.QPushButton(self.layoutWidget)
        self.calibration_Button.setObjectName("calibration_Button")
        self.action_layout.addWidget(self.calibration_Button)
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(340, 20, 151, 391))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.settings_layout = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.settings_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_layout.setObjectName("settings_layout")
        self.init_azim_sett_Button = QtWidgets.QDoubleSpinBox(self.layoutWidget1)
        self.init_azim_sett_Button.setMinimum(-360.0)
        self.init_azim_sett_Button.setMaximum(359.99)
        self.init_azim_sett_Button.setObjectName("init_azim_sett_Button")
        self.init_azim_sett_Button.setValue(0.0)
        self.settings_layout.addWidget(self.init_azim_sett_Button)
        self.init_zen_sett_Button = QtWidgets.QDoubleSpinBox(self.layoutWidget1)
        self.init_zen_sett_Button.setMinimum(-360.0)
        self.init_zen_sett_Button.setMaximum(360.0)
        self.init_zen_sett_Button.setObjectName("init_zen_sett_Button")
        self.init_zen_sett_Button.setValue(272.5)
        self.settings_layout.addWidget(self.init_zen_sett_Button)
        self.end_azim_sett_Button = QtWidgets.QDoubleSpinBox(self.layoutWidget1)
        self.end_azim_sett_Button.setMinimum(-360.0)
        self.end_azim_sett_Button.setMaximum(360.0)
        self.end_azim_sett_Button.setObjectName("end_azim_sett_Button")
        self.end_azim_sett_Button.setValue(360.0)
        self.settings_layout.addWidget(self.end_azim_sett_Button)
        self.end_zen_sett_Button = QtWidgets.QDoubleSpinBox(self.layoutWidget1)
        self.end_zen_sett_Button.setMinimum(-360.0)
        self.end_zen_sett_Button.setMaximum(360.0)
        self.end_zen_sett_Button.setObjectName("end_zen_sett_Button")
        self.end_zen_sett_Button.setValue(322.50)
        self.settings_layout.addWidget(self.end_zen_sett_Button)
        self.num_azim_steps_sett_Button = QtWidgets.QSpinBox(self.layoutWidget1)
        self.num_azim_steps_sett_Button.setObjectName("num_azim_steps_sett_Button")
        self.num_azim_steps_sett_Button.setValue(0)
        self.settings_layout.addWidget(self.num_azim_steps_sett_Button)
        self.num_zen_steps_sett_Button = QtWidgets.QSpinBox(self.layoutWidget1)
        self.num_zen_steps_sett_Button.setObjectName("num_zen_steps_sett_Button")
        self.num_zen_steps_sett_Button.setValue(20)
        self.settings_layout.addWidget(self.num_zen_steps_sett_Button)
        self.azim_vel_sett_Button = QtWidgets.QDoubleSpinBox(self.layoutWidget1)
        self.azim_vel_sett_Button.setMaximum(100.0)
        self.azim_vel_sett_Button.setObjectName("azim_vel_sett_Button")
        self.azim_vel_sett_Button.setValue(50.0)
        self.settings_layout.addWidget(self.azim_vel_sett_Button)
        self.zen_vel_sett_Button = QtWidgets.QDoubleSpinBox(self.layoutWidget1)
        self.zen_vel_sett_Button.setMaximum(100.0)
        self.zen_vel_sett_Button.setObjectName("zen_vel_sett_Button")
        self.zen_vel_sett_Button.setValue(50.0)
        self.settings_layout.addWidget(self.zen_vel_sett_Button)
        self.fixed_angle_rep_sett_Button = QtWidgets.QSpinBox(self.layoutWidget1)
        self.fixed_angle_rep_sett_Button.setObjectName("fixed_angle_rep_sett_Button")
        self.fixed_angle_rep_sett_Button.setValue(1)
        self.settings_layout.addWidget(self.fixed_angle_rep_sett_Button)
        self.save_settings_Button = QtWidgets.QPushButton(self.centralwidget)
        self.save_settings_Button.setGeometry(QtCore.QRect(500, 340, 141, 41))
        self.save_settings_Button.setObjectName("save_settings_Button")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(170, 20, 171, 391))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_5 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_7 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_7.setObjectName("label_7")
        self.verticalLayout.addWidget(self.label_7)
        self.label_6 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_6.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_6)
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.label_8 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_8.setObjectName("label_8")
        self.verticalLayout.addWidget(self.label_8)
        self.label_9 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_9.setObjectName("label_9")
        self.verticalLayout.addWidget(self.label_9)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.init_Button.setText(_translate("MainWindow", "Initialize"))
        self.set_zero_Button.setText(_translate("MainWindow", "Set zero"))
        self.single_start_Button.setText(_translate("MainWindow", "Move to angle"))
        self.disable_Button.setText(_translate("MainWindow", "Disable"))
        self.calibration_Button.setText(_translate("MainWindow", "Calibrate"))
        self.save_settings_Button.setText(_translate("MainWindow", "Save settings"))
        self.label_5.setText(_translate("MainWindow", "Initial azimuth angle"))
        self.label_2.setText(_translate("MainWindow", "Initial zenith angle"))
        self.label.setText(_translate("MainWindow", "Final azimuth angle"))
        self.label_7.setText(_translate("MainWindow", "Final zenith angle"))
        self.label_6.setText(_translate("MainWindow", "Number of azimuth steps"))
        self.label_3.setText(_translate("MainWindow", "Number of zenith steps"))
        self.label_4.setText(_translate("MainWindow", "Azimuth velocity"))
        self.label_8.setText(_translate("MainWindow", "Zenith velocity"))
        self.label_9.setText(_translate("MainWindow", "Repetitions time"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())