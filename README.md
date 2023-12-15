Цель: провести калибровку Датчика Солнца и Горизонта (ДСГ) - получить зависимость углов падающего луча от расстояния от центра матрицы датчика в виде полинома шестой степени, записать коэффициенты (A_0,..., A_6) в ДСГ.

Устройство калибратора включает в себя 4 модуля, разнесенных как физически, так и программно: датчик Солнца (Sensor), повортоное устройство (Rotator), источник питания и обработчник данных.
![image](https://github.com/functiod/Calibrator/assets/113659575/794b8001-9071-4d8d-be4f-bc606dcee2f5)

Датчик Солнца управляется библиотекой Pyserial. Он принимает на вход команду, которая определяет выполняемое действие - сделать фотографию, найти значение угла падения солнечного луча и т.д -
и возвращает посылку с соответствующими данными, например [угол азимут, угол зенит, x координата луча на матрице, y координата луча на матрице].
![image](https://github.com/functiod/Calibrator/assets/113659575/b0a51e34-cc1d-4069-b1e2-0816b00f7054)


Поворотное устройство управляется низкоуровневыми библиотеками, написанными на C и C++ производителем ротатора. Для удобства использования библиотеки были переписаны на языке Python в модуле acspy_lib.
![image](https://github.com/functiod/Calibrator/assets/113659575/767cf6df-5d58-42d4-8e0d-f31db63f1d14)

Источник питания HMP4040 управляется программой, написанной на Python, через Ethernet интерфейс. Источник запитывает ДСГ и имитатор Солнца, стоящие на оптическом-экспериментальном стенде.
![image](https://github.com/functiod/Calibrator/assets/113659575/8edd2edf-60c3-4452-9560-cbfd173ef725)

Имитатор Солнца представляет собой светодиод мощности 60 Вт, выдающий монохроматичный коллимированный пучок света с угловым размером 0.5 градусов.

Доступ к каждому модулю осуществляется через одноплатный компьютер Raspberry pi.
![image](https://github.com/functiod/Calibrator/assets/113659575/10f72e2a-edc4-480f-8063-372299463430)

Методика калибровки:
1) Ротатор находит положение, в котором луч от имитатра Солнца располагается соосно с ДСГ;