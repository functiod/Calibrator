import serial               #pyserial
import cv2                  #opencv-python
import numpy as np
import time
import datetime
import struct
import crcmod               #crcmod
import math
from PIL import Image       #pillow-PIL
from PIL import ImageFont
from PIL import ImageDraw
from dataclasses import dataclass

# настройки матрицы видимого диапазона
lupa300_set = { 'addr_rec'          : 0x03,         #адрес датчика которому адресована команда
                'addr_send'         : 0xF0,         #адрес отправителя, для получения ответа по этому адресу
                                                    #             | установка 1   | установка 2   | установка 3 |
                'integration_time'  : 1000,           #выдержка, лин|   50          |  4            |             |
                'res1_lenght'       : 0,
                'ft_timer'          : 0,
                'vcal'              : 74, # 0x4A,         #0x4A         |   0x60        |  0x90         |             |
                'vblack'            : 160, #0x6B,         #0x06B        |   0x70        |  0x70         |             |
                'voffset'           : 85, #0x55,           #0x19         |   0x20        |  0x20         |             |
                'pga_setting'       : 1968,#0x0FB0,       #0x0FA0       | 0x0FA0        |  0x0FA0       |             |
                #'lupa_clk'          : 1500,         #             |   1500        |  80           |             |
                'black_level'       : 10,           # в % от максимального значения
                'stm_temperature'   : -128,         # начальное значение температуры
}
x_sens = 0.0
y_sens = 0.0
zen_sens = 0.0
azim_sens = 0.0

test_center_x = 300
test_center_y = 300
bg_noise = 0
salt_noise = 0

# констатны определяются калибровкой
x0 = 319.298
y0 = 242.938
A = -3.91E-13
B = 3.05E-10
C = -8.38E-08
D = 9.88E-06
E = -1.23E-03
F = 4.43E-01
G = 0.0
phi0 = 0.5
k_phi = 1.0

#массив для передачи калибровок датчику
calib_coeff = [
    G, F, E, D, C, B, A,
    x0, y0, phi0,
    k_phi, 3.0                # a1, b1
    ]

# настройки матрицы ИК диапазона
emissivity = 97             # в %
reflection_temp = 2301      # в сотых долях градуса (2301 == 23.01С)
resolution = 3              # 0 - 16bit, 1 - 17bit, 2 - 18bit, 3 - 19bit
ref_rate = 3                # 0 - 0.5 Гц, 1 - 1 Гц, 2 - 2 Гц, 3 - 4 Гц, 4 - 8 Гц, 5 - 16 Гц, 6 - 32 Гц, 7 - 64 Гц
mode = 1                    # 0 - выключение между измерениями, 1 - постоянно включен

# настройки дуса, акселя и мага
gam_mode = 3
gam_smplrt_div = 9
g_full_scale = 3
g_dlpf_cfg = 3
g_lp_mode_cfg = 0
a_full_scale = 0
a_dec2_cfg = 0
a_dlpf_cfg = 3
m_odr = 1

# данные дуса, акселя и мага


#открытие порта
ser = serial.Serial()
ser.baudrate = 1000000
ser.port = 'COM3' #COM11 & #COM4
ser.timeout = 5
ser.open()

prev_time = datetime.datetime.now()

def main():
    global ref_rate, gam_mode
    global test_center_x, test_center_y, bg_noise, salt_noise
    #testRotStand()
    #setNewSensAddr(lupa300_set, 0xFF, 0x06)
    #getCalibCoeff(lupa300_set)
    #setSettingsMatrix(lupa300_set)
    #setCalibCoeff(calib_coeff, lupa300_set)
    #getCalibCoeff(lupa300_set)
    #testFileName()
    setGamSettings(lupa300_set)
    setSettingsMatrix(lupa300_set)
    #getFWversion(lupa300_set)
    #calcCrc16()


    #time.sleep(1)

    i = 0
    while i < 6:
        print("")
        print("#", i)
        #getFWversion(lupa300_set)
        setGamSettings(lupa300_set)
        getSensorTemperature(lupa300_set)
        #getMagData(lupa300_set)
        #getGyroAccData(lupa300_set)
        #BroadcastTest(lupa300_set)
        # getMlxPhoto(lupa300_set)
        #setSettingsMatrix(lupa300_set)
        saveImageToFile(getImg10bit(lupa300_set, cmd=0x04, v_size=480, h_size=480), lupa300_set)
        #testSensorCenterAngles()

        time.sleep(1)
        if lupa300_set['addr_rec'] > 5:
            lupa300_set['addr_rec'] = 1
        else:
            lupa300_set['addr_rec'] += 1
        #lupa300_set['integration_time'] += 10
        #lupa300_set['vcal'] += 10
        #test_center_x += 1
        #test_center_y += 2
        i += 1

def ScanPort(set):
    for i in range(255):
        print(i, end='\t')


def BroadcastTest(set):
    print("")
    print("#BroadcastTest")
    # установка таймаута и очистка буфера
    ser.timeout = 1
    ser.flushInput()

    # запрос данных с гироскопа и магнитометра широковещательным пакетом
    ser.write(
        addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x65, 0x00, 0x00, 0, 0]))
    ser.write(
        addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x44, 0x00, 0x00, 0, 0]))
    time.sleep(0.2)

    ser.write(
        addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x28, 0x00, 0x00, 0, 0]))

    tmp_buf = ser.read(31)
    if len(tmp_buf) < 31:
        print("WARNING: GYRO request timeout.")
        return
    m_x = struct.unpack('<H', tmp_buf[8: 10])[0]
    m_y = struct.unpack('<H', tmp_buf[10: 12])[0]
    m_z = struct.unpack('<H', tmp_buf[12: 14])[0]

    a_x = struct.unpack('<h', tmp_buf[15: 17])[0]
    a_y = struct.unpack('<h', tmp_buf[17: 19])[0]
    a_z = struct.unpack('<h', tmp_buf[19: 21])[0]
    temp = struct.unpack('<h', tmp_buf[21: 23])[0]/326.8 + 25
    g_x = struct.unpack('<h', tmp_buf[23: 25])[0]
    g_y = struct.unpack('<h', tmp_buf[25: 27])[0]
    g_z = struct.unpack('<h', tmp_buf[27: 29])[0]

    print("Mag data: %.2f\t%.2f\t%.2f" % (m_x-32768, m_y-32768, m_z-32768))
    print("Acc data: %.2fg\t%.2fg\t%.2fg" % (a_x/16384, a_y/16384, a_z/16384))
    print("Gyro data: ", g_x, g_y, g_z)
    print("Gyro temp = %.1f°C" % temp)

    getSensorTemperature(set)

    #запрос углов
    ser.write(addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00]))

    rx_buf = ser.read(30)  # получаем центр и углы с ДСГ
    if packVerification(set, rx_buf):
        print("WARNING: Angles packet is corrupted.")
    else:
        if rx_buf[8:13] == b'ERROR':
            print("WARNING: SS photo received ERROR.")
            return
        x_sens = struct.unpack(   '<f', rx_buf[8:12])[0]
        y_sens = struct.unpack(   '<f', rx_buf[12:16])[0]
        zen_sens = struct.unpack( '<f', rx_buf[16:20])[0]
        azim_sens = struct.unpack('<f', rx_buf[20:24])[0]
        print("SS center:  \t%.2f\t%.2f\t" % (x_sens, y_sens))
        print("SS angles:  \t%.2f\t%.2f\t" % (zen_sens, azim_sens))

def setNewSensAddr(set, old_addr, new_addr):
    """
        Функция установки нового адреса датчику. Адрес сохраняется во флешь.
    """
    tx_pack = [0xAA, old_addr, set['addr_send'], 0x00, 0x00, 0x05, 1, 0, new_addr, 0, 0]
    ser.timeout = 4
    ser.flushInput()
    ser.write(addCrc16(tx_pack))
    pac = ser.read(10)
    if packVerification(set, pac):
        return
    if pac[5] == 0x85:
        print("MO address has been changed. New address:", pac[2])
        set['addr_rec'] = pac[2]

def getFWversion(set):
    ser.timeout = 0.1
    ser.flushInput()
    ser.write(
        addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x0B, 0x00, 0x00, 0, 0]))
    pac = ser.read(30)
    packVerification(set, pac)
    print("FW version = %s" % pac[8:-2])

def packVerification(set, packet):
    #for it in packet:
    #    print("0x%X" % it, end=' ')
    #print("")
    if len(packet) == 0:
        print("WARNING. Packet is absent.")
        return 1
    if packet[0] != 0xAA:
        print("WARNING. Packet preambula is absent.")
        return 1
    if packet[1] != set['addr_send']:
        print("WARNING. Received address is wrong.")
        return 1

    num_byte = packet[7] << 8 | packet[6]
    if (num_byte + 10) != len(packet):
        print("WARNING. Packet size is too large. num_bytes = %d" % num_byte)
        return 1

    crc_pack = packet[8 + num_byte + 1] << 8 | packet[8 + num_byte]
    crc16_fun = crcmod.mkCrcFun(0x18005, 0xFFFF)
    crc_word = crc16_fun(serial.to_bytes(packet[:-2]))

    #print("num_bytes = 0x%X" % num_byte)
    #print("received crc = 0x%X" % crc_pack)
    #print("calculated crc = 0x%X" % crc_word)
    if crc_pack != crc_word:
        print("WARNING. Received CRC16 is wrong.")
        return 1

    #print("Packet is OK")
    return 0

def getGyroAccData(set):
    global prev_time
    # установка таймаута и очистка буфера
    ser.timeout = 1
    ser.flushInput()

    # запрос данных с гироскопа
    tx_pac = addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x24, 0x00, 0x00, 0, 0])

    delta = datetime.datetime.now() - prev_time
    prev_time = datetime.datetime.now()
    print("%.3f" % (delta.seconds + delta.microseconds / 1000000), end='\t')
    myArrPrint(tx_pac)
    print('')

    ser.write(tx_pac)
    tmp_buf = ser.read(24)

    delta = datetime.datetime.now() - prev_time
    prev_time = datetime.datetime.now()
    print("%.3f" % (delta.seconds + delta.microseconds / 1000000), end='\t')
    myArrPrint(tmp_buf)
    print('')

    if len(tmp_buf) < 24:
        myArrPrint(tmp_buf)
        print("WARNING: GYRO request timeout.")
        return
    a_x = struct.unpack('<h', tmp_buf[8: 10])[0]
    a_y = struct.unpack('<h', tmp_buf[10: 12])[0]
    a_z = struct.unpack('<h', tmp_buf[12: 14])[0]
    temp = struct.unpack('<h', tmp_buf[14: 16])[0]/326.8 + 25
    g_x = struct.unpack('<h', tmp_buf[16: 18])[0]
    g_y = struct.unpack('<h', tmp_buf[18: 20])[0]
    g_z = struct.unpack('<h', tmp_buf[20: 22])[0]
    print("Acc data: %.2fg\t%.2fg\t%.2fg" % (a_x/16384, a_y/16384, a_z/16384))
    print("Gyro data: ", g_x, g_y, g_z)
    print("Gyro temp = %.1f°C" % temp)
    #print("")

def getMagData(set):

    #установка таймаута и очистка буфера
    ser.timeout = 1
    ser.flushInput()

    # запрос данных с магнитометра
    ser.write(
        addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x23, 0x00, 0x00, 0, 0]))

    tmp_buf = ser.read(17)
    if len(tmp_buf) < 17:
        print("WARNING: MAG request timeout.")
        return

    #print(tmp_buf)
    m_x = struct.unpack('<H', tmp_buf[8: 10])[0]
    m_y = struct.unpack('<H', tmp_buf[10: 12])[0]
    m_z = struct.unpack('<H', tmp_buf[12: 14])[0]
    m_t = tmp_buf[14] * 0.7 - 75
    print("Mag data: %.1fuT\t\t%.1fuT\t\t%.1fuT\t\tMag temp = %.1f°C" %
          ((m_x-32768)/40.96, (m_y-32768)/40.96, (m_z-32768)/40.96, m_t))

def setGamSettings(set):
    global prev_time
    # настройка GAM
    tmp_buf = addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x20, 0x09, 0x00,
                  gam_mode, gam_smplrt_div,
                  g_full_scale, g_dlpf_cfg, g_lp_mode_cfg,
                  a_full_scale, a_dec2_cfg, a_dlpf_cfg, m_odr,
                  0, 0])
    ser.write( tmp_buf )

    delta = datetime.datetime.now() - prev_time
    prev_time = datetime.datetime.now()
    print("%.3f" % (delta.seconds + delta.microseconds / 1000000), end='\t')
    myArrPrint(tmp_buf)
    time.sleep(0.25)

    # настройка ДГ
    packet = addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x11, 0x06, 0x00, emissivity,
                   reflection_temp & 0xFF, reflection_temp >> 8, resolution, ref_rate, mode, 0, 0])
    # for c in packet:
    #     print(hex(c), end=' ')
    # print()
    ser.write(packet)
    time.sleep(0.5)
    print('')

def getMlxPhoto(set):
    h_size = 32
    v_size = 24

    # очистка входного буфера
    # time.sleep(0.1)
    ser.timeout = 7

    # запрос фото от ДГ
    print('IR photo receiving data...')
    photo = bytearray()

    ser.flushInput()  # очистка входного буфера
    ser.write(addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0, 0, 0x13, 0x00, 0x00, 0, 0]))

    temp_buff = ser.read(10)
    if temp_buff[8] == 0x45 and temp_buff[9] == 0x52: #ER
        print('ERROR. OM returned HS error.')
        return
    else:
        temp_buff += ser.read(24 * 32 * 4)
        if packVerification(set, temp_buff):
            print('WARNING. Packet is corrupted.')
            return
    photo += temp_buff[8:-2]
    photo = np.frombuffer(photo, dtype='<f')
    photo.shape = (24, 32)

    # преобразование массива для наглядности
    up_level = 255
    min_t = photo.min()
    max_t = photo.max()
    photo = (photo - min_t) * up_level / (max_t - min_t)

    print('IR photo has been received.')
    print("Min temp = %.1f°C" % min_t)
    print("Max temp = %.1f°C" % max_t)

    #сохранение
    photo8bit = photo.astype(np.uint8)
    img = Image.fromarray(photo8bit)
    time_now = datetime.datetime.now()
    filename = time_now.strftime("PHOTO\\%Y-%m-%d %H-%M-%S IRphoto ")
    filename += "RR=%d RS=%d EM=%d RT=%.2f MIN=%.2f MAX=%.2f.png" % \
                (ref_rate, resolution, emissivity, reflection_temp/100, min_t, max_t)
    img.save(filename)
    print("IR photo saved.")
    #print("")

def testFileName():
    filename = datetime.datetime.now()
    str = filename.strftime("PHOTO\\%Y-%m-%d %H-%M-%S IRphoto ")
    str += "RR=%d RS=%d EM=%d RT=%.2f.png" % (ref_rate, resolution, emissivity, reflection_temp/100)
    print(str)

def getPhoto(set):
    """
        Функция для получения фото с датчика. Просто фото. Для быстрой проверки настроек матрицы.
    """
    setSettingsMatrix(set)
    saveImageToFile(getImg8bit(), set)

def getSensorAngles(set, cmd = 0x05):
    """
        Функция запрашивает координаты центра и рассчитанные углы у датчика.
        Печатает в консоль время запроса, адрес датчика и полученные углы.
        На входе получает cmd - команда запроса углов. сmd может быть:
        0х05 - по умолчанию, расчет углов по кускам нескольких фото, полученных на максимальной частоте опроса
            матрцы - 1500 кГц, на такой частоте меньше шума, особенно при высоких температурах
        0x04 - по желанию, расчет углов по целому фото, но на низкой частоте - 100 кГц. Частота должна быть задана
            извне.
    """
    time.sleep(0.1)
    ser.timeout = 30
    ser.flushInput()
    ser.write(addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, cmd, 0x00, 0x00, 0x00, 0x00]))
    rx_buf = ser.read(26)
    if len(rx_buf) < 26:
        print("WARNING: Angles. Answer timed out.")
        return
    x_sens = struct.unpack(   '<f', rx_buf[8:12])[0]
    y_sens = struct.unpack(   '<f', rx_buf[12:16])[0]
    zen_sens = struct.unpack( '<f', rx_buf[16:20])[0]
    azim_sens = struct.unpack('<f', rx_buf[20:24])[0]
    print(datetime.datetime.now().strftime("%H-%M-%S"), set['addr_rec'], "%.3f°\t%.3f°" % (zen_sens, azim_sens), sep='\t')

def testSensorMainArrays():
    """
        Функция для анализа главных массивов сумм и отладки процесса расчета центро пятна. Получает от датчика фото и
        рассчитанные по этому фото массивы. Выводит разницу массивов, расчитанных датчиком и расчитанных на ПК.
    """
    setSettingsMatrix()

    gray = getImg10bit(0x10)
    #print(gray[0:5][0:5])
    gray = processingImg(gray)
    #print(gray[0:5][0:5])

    x_sum_pc = gray.sum(axis=0)
    y_sum_pc = gray.sum(axis=1)
    x_sum_sens = getMainArray('X')
    y_sum_sens = getMainArray('Y')
    #print(y_sum_sens)
    #print(y_sum_pc)
    print(x_sum_pc - x_sum_sens)
    print(y_sum_pc - y_sum_sens)

def testSensorCenterAngles():
    """
        Функция для анализа главных массивов сумм и отладки процесса расчета центра пятна. Получает от датчика фото и
        рассчитанные по этому фото центр пятна и углы. Выводит расчеты датчика и результат сравнения расчетов датчика с
        расчитами ПК. Сохраняет фото в файл.
    """
    setSettingsMatrix(lupa300_set)

    gray = getImg10bit(lupa300_set, cmd=0x03, v_size=480, h_size=480)

    x_pc, y_pc = calcCenter(gray)
    zen_pc, azim_pc = F_angles(x_pc, y_pc)

    print("sens:  \t%.3f\t%.3f\t\t%.3f°\t%.3f°\t" % (x_sens, y_sens, zen_sens, azim_sens))
    print("pc:    \t%.3f\t%.3f\t\t%.3f°\t%.3f°\t" % (x_pc, y_pc, zen_pc, azim_pc))
    print("dif2pc:\t%.3f\t%.3f\t\t%.3f°\t%.3f°\t" % (x_sens - x_pc, y_sens - y_pc, zen_sens - zen_pc, azim_sens - azim_pc))
    saveImageToFile(gray, lupa300_set)

def processingImg(arr, set):
    """
        Функция обработки изображения. Медианный фильтр + отсечение заданного уровня черного. На входе и на выходе
        матрицы.
    """

    #обработка изображения
    max = np.max(arr)  # обработка изображения, выбор наиболее яркой области
    print("max = ", max)

    arr.shape = (480, 480)
    arr = cv2.medianBlur(arr, ksize=3)
    arr = np.where(arr > (max * set['black_level'] / 100), arr, 0)

    return arr

def calcCenter(arr):
    """
        Функция расчета центра пятна методом центра масс по всему изображению. На входе матрица, на выходе 2 координаты.
    """

    arr = processingImg(arr, lupa300_set)
    height, width = arr.shape
    print("height, width = ", height, width)
    # нахождение координаты центра пятна как координаты центра масс
    X = np.linspace(0, width - 1, width)
    Y = np.linspace(0, height - 1, height)
    X, Y = np.meshgrid(X, Y)
    if np.sum(arr) == 0:
        print("WARNING: np.sum(arr) == 0 ")
        return 0, 0
    x = np.sum(arr * X) / np.sum(arr)
    y = np.sum(arr * Y) / np.sum(arr)

    return x, y

def printProgressBar(percent, num_bytes):
    """
        Функция отрисовки прогресс бара в консоль. На входе процент 0-100, на выходе отрисовка в консоль.
    """
    if percent > 100:
        return 0
    str = "|"
    i = 0
    while i < 50:
        if i < (percent / 2):
            str += "/"
        else:
            str += "-"
        i += 1
    str += "|"
    print("\r%s %d" % (str, percent) + '%\t' + "%d" % num_bytes, end='')

def getImg8bit(set, cmd = 0x02):
    """
        Функция запроса 8ми битного изображения с датчика. В процессе выкачки рисует прогресс бар в консоль. Установлен
        таймаут на ожидание байтов из порта.
        cmd может быть:
        0х02 - по умолчанию. Просто получение картинки.
        0х0F - после выдачи картинки, датчик выдает пакет с расчитанными центром и углами по этой картинке 26 байт
        возвращает матрицу 640*480 uint8_t
    """

    # запрос и получение координаты пятна
    time.sleep(0.1)
    ser.timeout = 60
    ser.flushInput()  # очистка входного буфера

    ser.write(addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, cmd, 0x00, 0x00, 0x00, 0x00]))
    i = 0
    photo = bytearray()
    while i < 480:
        photo += ser.read(640)
        i += 1
        printProgressBar(100 * i / 480)
    print('')
    photo = np.frombuffer(photo, dtype=np.uint8)
    photo.shape = (480, 640)
    return photo

def getImg10bit(set, cmd = 0x03, h_size = 640, v_size = 480):
    """
        Функция запроса 10ти битного изображения с датчика. В процессе выкачки рисует прогресс бар в консоль. Установлен
        таймаут на ожидание байтов из порта.
        cmd может быть:
            0х03 - по умолчанию. Просто получение картинки.
            0х10 - после выдачи картинки, датчик выдает пакет с расчитанными центром и углами по этой картинке 26 байт
        h_size - высота фото
        v_size - ширина фото
        возвращает матрицу 640*480 uint16_t
    """
    global x_sens, y_sens, zen_sens, azim_sens
    global test_center_x, test_center_y, bg_noise, salt_noise

    # запрос и получение координаты пятна
    time.sleep(0.1)
    ser.timeout = 3
    ser.flushInput()  # очистка входного буфера

    #запрос расчета углов по картинке, реальной или синтетической
    ser.write(addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, cmd, 0x08, 0x00,
                        test_center_x & 0x00FF, test_center_x >> 8,
                        test_center_y & 0x00FF, test_center_y >> 8,
                        bg_noise & 0x00FF, bg_noise >> 8,
                        salt_noise & 0x00FF, salt_noise >> 8, 0x00, 0x00]))

    rx_buf = ser.read(30)  # получаем центр и углы с ДСГ
    if packVerification(set, rx_buf):
        print("WARNING: Angles packet is corrupted.")
    else:
        if rx_buf[8:13] == b'ERROR':
            print("WARNING: SS photo received ERROR.")
            return
        x_sens = struct.unpack(   '<f', rx_buf[8:12])[0]
        y_sens = struct.unpack(   '<f', rx_buf[12:16])[0]
        zen_sens = struct.unpack( '<f', rx_buf[16:20])[0]
        azim_sens = struct.unpack('<f', rx_buf[20:24])[0]
        print("SS center:  \t%.2f\t%.2f\t" % (x_sens, y_sens))
        print("SS angles:  \t%.2f\t%.2f\t" % (zen_sens, azim_sens))

    ser.timeout = 0.1

    print("SS photo receiving data...")
    i = 0
    j = 0
    bytes1 = 0
    photo = bytearray()
    while i < v_size:
        if j > 3:
            print("\r\nWARNING: Photo. Number of requests exceeded.")
            return

        ser.flushInput()  # очистка входного буфера
        ser.write(addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0, 0, 0x02, 0x02, 0x00, i & 0x00FF, i >> 8, 0, 0]))

        temp_buff = ser.read(h_size * 2 + 10)
        if packVerification(set, temp_buff):
            j += 1
            continue
        j = 0

        bytes1 += len(temp_buff) - 10
        printProgressBar(100 * (i + 1) / v_size, bytes1)
        photo += temp_buff[8:-2]
        i += 1

    excess_bytes = 0
    while ser.read(1):
        excess_bytes += 1
    if excess_bytes:
        print("Excess bytes = %d" % excess_bytes)

    photo = np.frombuffer(photo, dtype=np.uint16)
    photo.shape = (v_size, h_size)
    print("")
    return photo

def convertImageTo8bit(arr):
    """
        Функция конвертации матрицы в uint8_t для сохранения фото в файл
    """
    for x in arr:
        x >>= 2
    return np.array(arr, dtype=np.uint8)

def getSensorTemperature(set):
    """
        Функция запроса температуры у датчика
    """
    # запрос температуры
    time.sleep(0.1)
    ser.timeout = 1
    ser.flushInput()
    ser.write(addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x0A, 0x00, 0x00, 0x00, 0x00]))
    tmp_buf = ser.read(11)
    if packVerification(set, tmp_buf):
        print("WARNING: Temperature request timeout.")
        lupa300_set['stm_temperature'] = -128
    else:
        lupa300_set['stm_temperature'] = tmp_buf[8]
        print("STM temp = %d°C" % lupa300_set['stm_temperature'])
    #print("")
    return lupa300_set['stm_temperature']

def getMainArray(param, set):
    """
        Функция выкачки главных массивов сумм, по которым затем считаются центры масс. Необходима для отладки алгоритма
        расчета. В качестве параметра принимает 'X' или 'Y' соответственно для выкачки 640 или 480 данных uint32_t
    """
    #вычисление команды запроса
    cmd = 0x08
    num_bytes = 640 * 4
    if param == 'Y':
        cmd += 1
        num_bytes = 480 * 4

    # запрос основного массива для расчета центра тяжести
    time.sleep(0.1)
    ser.timeout = 5
    ser.flushInput()
    ser.write(addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, cmd, 0x00, 0x00, 0x00, 0x00]))
    tmp_buf = ser.read(num_bytes)
    if len(tmp_buf) < num_bytes:
        print("WARNING: Array request timeout.")
        return -128
    else:
        tmp_buf = np.frombuffer(tmp_buf, dtype=np.uint32)
        return tmp_buf

def setSettingsMatrix(set):
    """
        Функция настройки матрицы. Все параметры задаются в начале файла. Настраиваются матрица, частота ее опроса и
        уровень черного для отсечения темных пикселей.
    """
    # расчет res1_lenght и ft_timer по заданной выдержке integration_time
    if set['integration_time'] > 479:
        set['res1_lenght'] = 4
    else:
        set['res1_lenght'] = 484 - set['integration_time']
    set['ft_timer'] = set['res1_lenght'] + set['integration_time']

    # настройка параметров матрицы
    ser.write(
        addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x01, 0x09, 0x00, set['res1_lenght'] & 0xFF,
                  set['res1_lenght'] >> 8, set['ft_timer'] & 0xFF, set['ft_timer'] >> 8, set['vcal'], set['vblack'],
                  set['voffset'], set['pga_setting'] & 0xFF, set['pga_setting'] >> 8, 0x00, 0x00]))
    # настройка частоты опроса матрицы
    #ser.write(
    #    addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x07, 0x02, 0x00, set['lupa_clk'] & 0xFF,
    #              set['lupa_clk'] >> 8, 0, 0]))

    # настройка уровня черного пикселя
    ser.write(
        addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x0C, 0x01, 0x00, set['black_level'], 0, 0]))

def saveImageToFile(photo_in, set):
    """
        Функция сохранения матрицы в файл - получается фото. В фото добавляется текстовая информация о настройках
        датчика в левый верхний угол. Файл сохраняется с индивидуальным именем, состоящим из текущей даты и времени.
    """

    # -------------------------сохранение фото в файл------------------------------------------------------------------
    if photo_in is None:
        print("WARNING: Photo cannot be saved.")
        print("")
        return
    if photo_in.itemsize != 1:
        photo_in = convertImageTo8bit(photo_in)

    # объекты для текстовой надписи
    h_text = 12  # высота текста в картинке
    text_font = ImageFont.truetype("courbd.ttf", h_text)
    text_img = Image.new("RGBA", (h_text * 16, h_text * len(set)), (0, 0, 0))
    text_draw = ImageDraw.Draw(text_img)

    # отрисовка надписей
    i = 0
    for name, val in set.items():
        text_draw.text((3, h_text * i), '{0} : {1}'.format(name,val), (255, 255, 255), font=text_font)
        i += 1

#    text_draw.text((3, h_text * 0), "STM32 tmprt:   %d°C" % stm_temperature, (255, 255, 255), font=text_font)
#    text_draw.text((3, h_text * 1), "RES1 LENGTH:   0x%X" % res1_lenght, (255, 255, 255), font=text_font)
#    text_draw.text((3, h_text * 2), "FT TIMER:      0x%X" % ft_timer, (255, 255, 255), font=text_font)
#    text_draw.text((3, h_text * 3), "VCAL:          0x%X" % vcal, (255, 255, 255), font=text_font)
#    text_draw.text((3, h_text * 4), "VBLACK:        0x%X" % vblack, (255, 255, 255), font=text_font)
#   text_draw.text((3, h_text * 5), "VOFFSET:       0x%X" % voffset, (255, 255, 255), font=text_font)
#    text_draw.text((3, h_text * 6), "PGA SETTING:   0x%X" % pga_setting, (255, 255, 255), font=text_font)
#    text_draw.text((3, h_text * 7), "LUPA clock:   %dkHz" % lupa_clk, (255, 255, 255), font=text_font)
#    text_draw.text((3, h_text * 8), "Sens address:  %d"   % addr_rec, (255, 255, 255), font=text_font)

    del text_draw
    del text_font

    # вставка надписей в фото и сохранение
    img = Image.fromarray(photo_in)
    img.paste(text_img, (0, 0), text_img)
    filename = datetime.datetime.now()
    img.save(filename.strftime("PHOTO\\%Y-%m-%d %H-%M-%S photo.png"))
    print("SS photo saved.")
    print("")


def setRotStandAngle(axis, angle, addr):
    """
        Функция установки поворотного устройства в требуемое положение.
        axis - ось вращения
            'V' - вертикальная ось
            'H' - горизонтальная ось
        angle - угол -90...90 градусов
    """
    cmd = 0x70
    if axis == 'H':
        cmd += 0x01
    if angle > 90 or angle < -90:
        return
    pulse_width = int(500 + 2000 / 180 * (angle + 90))
    ser.write(addCrc16([0xAA, 0xFE, addr, 0x00, 0x00, cmd, 0x02, 0x00, pulse_width & 0xFF, pulse_width >> 8,
                        0x00, 0x00]))

def testRotStand():
    """
        Функция тестирования поворотного устройства
    """
    #setRotStandAngle('V', -60)
    #setRotStandAngle('H', 60)
    #time.sleep(2)
    #setRotStandAngle('V', 60)
    #setRotStandAngle('H', -60)
    #time.sleep(2)

    setRotStandAngle('V', 0)
    setRotStandAngle('H', 0)
    time.sleep(1)
    h = -70
    while h <= 70:
        setRotStandAngle('H', h)
        time.sleep(0.2)
        setRotStandAngle('V', 70)
        time.sleep(0.5)
        setRotStandAngle('V', -70)
        time.sleep(0.5)
        h += 10
    setRotStandAngle('V', 0)
    setRotStandAngle('H', 0)

def addCrc16(str):
    """
        Функция расчета CRC16 для пакета. На вход принимает пакет, байты CRC должны присутствовать, так как функция
        записывает CRC на место последних двух байт.
        Name  : CRC-16
        Poly  : 0x8005    x^16 + x^15 + x^2 + 1
        Init  : 0xFFFF
        Revert: true
        XorOut: 0x0000
        Check : 0x4B37 ("123456789")
        MaxLen: 4095 byte (32767 bit) - detect single, double, triple and all odd errors
    """

    crc16_fun = crcmod.mkCrcFun(0x18005, 0xFFFF)
    crc_word = crc16_fun(serial.to_bytes(str[:-2]))
    str[-2] = crc_word & 0x00FF
    str[-1] = crc_word >> 8
    return str

def myArrPrint(arr):
    print("[", end='')
    for x in arr:
        print(format(x, '02X'), end='\t')
    print("]", end='')

def calcCrc16():
    print("Get SS data")
    pac = [0xAA, 0x01, 0x0F, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00]
    myArrPrint(addCrc16(pac))

    print("Read SS data")
    pac = [0xAA, 0x01, 0x0F, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00]
    myArrPrint(addCrc16(pac))

    print("Broadcast get SS data")
    pac = [0xAA, 0x00, 0x00, 0x00, 0x00, 0x44, 0x00, 0x00, 0x00, 0x00]
    myArrPrint(addCrc16(pac))


    '''
    pac = [0xAA, 0x01, 0x02, 0x00, 0x00, 0x23, 0x00, 0x00, 0, 0]
    myArrPrint(addCrc16(pac))

    print("Calculate centers with sinthetyc photo:")
    pac = [0xAA, 0x01, 0xFF, 0x00, 0x00, 0x03, 0x08, 0x00, 0x64, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    myArrPrint(addCrc16(pac))

    print("Get FW version:")
    pac = [0xAA, 0x01, 0xFF, 0x00, 0x00, 0x0B, 0x00, 0x00, 0x00, 0x00]
    myArrPrint(addCrc16(pac))

    print("Get first line:")
    pac = [0xAA, 0x01, 0xFF, 0, 0, 0x02, 0x02, 0x00, 0, 0, 0, 0]
    myArrPrint(addCrc16(pac))

    print("Set addr = 2:")
    pac = [0xAA, 1, 0xFF, 0x00, 0x00, 0x05, 1, 0, 2, 0, 0]
    myArrPrint(addCrc16(pac))

    print("Set addr = 1:")
    pac = [0xAA, 2, 0xFF, 0x00, 0x00, 0x05, 1, 0, 1, 0, 0]
    myArrPrint(addCrc16(pac))

    print("Set addr = 1:")
    pac = [0xAA, 0xFF, 0xFF, 0x00, 0x00, 0x05, 1, 0, 1, 0, 0]
    myArrPrint(addCrc16(pac))

    print("Get mlx photo line:")
    pac = [0xAA, 0x01, 0xFF, 0, 0, 0x13, 0x02, 0x00, 0, 0, 0, 0]
    myArrPrint(addCrc16(pac))

    pac = [0xAA, 0x01, 0xFF, 0x00, 0x00, 0x11, 0x06, 0x00, 0x5F, 0xC4, 0x09, 0x03, 0x06, 0x00, 0x00, 0x00]
    myArrPrint(addCrc16(pac))

    pac = [0xAA, 0x01, 0xFF, 0x00, 0x00, 0x12, 0x00, 0x00, 0x00, 0x00]
    myArrPrint(addCrc16(pac))

    pac = [0xAA, 0x01, 0xFF, 0x00, 0x00, 0x13, 0x00, 0x00, 0x00, 0x00]
    myArrPrint(addCrc16(pac))

    pac = [0xAA, 0x02, 0xFF, 0x00, 0x00, 0x21, 0x00, 0x00, 0x00, 0x00]
    myArrPrint(addCrc16(pac))
    '''


def setCalibCoeff(coeff_arr, set):
    """
        Функция передачи датчику данных калибровки. На вход принимает список параметров. Датчик по приему этих данных
        сразу записывает их во флешку (энергонезависимую память).
    """
    tx_pack = [0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x0D, 48, 0]

    for element in coeff_arr:
        tx_pack += struct.pack('<f', element)

    tx_pack += [0, 0]
    ser.write(addCrc16(tx_pack))
    time.sleep(3)
    #print(tx_pack)

def getCalibCoeff(set):
    """
        Функция запрашивает у датчика его данные калибровки и выводит их в консоль.
    """
    # проверка записанных переменных
    time.sleep(0.1)
    ser.timeout = 1
    ser.flushInput()
    ser.write(addCrc16([0xAA, set['addr_rec'], set['addr_send'], 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00, 0x00]))
    rx_pack = ser.read(90)

    if len(rx_pack) < 90:
        print("WARNING: Calibration coefficients request timeout.")
        return

    print("A =  \t%G" % struct.unpack('<f', rx_pack[32: 36])[0])
    print("B =  \t%G" % struct.unpack('<f', rx_pack[28: 32])[0])
    print("C =  \t%G" % struct.unpack('<f', rx_pack[24: 28])[0])
    print("D =  \t%G" % struct.unpack('<f', rx_pack[20: 24])[0])
    print("E =  \t%G" % struct.unpack('<f', rx_pack[16: 20])[0])
    print("F =  \t%G" % struct.unpack('<f', rx_pack[12: 16])[0])
    print("G =  \t%G" % struct.unpack('<f', rx_pack[ 8: 12])[0])

    print("x0 =  \t%.3f" % struct.unpack('<f', rx_pack[36: 40])[0])
    print("y0 =  \t%.3f" % struct.unpack('<f', rx_pack[40: 44])[0])
    print("phi0 =\t%.3f" % struct.unpack('<f', rx_pack[44: 48])[0])
    print("a1 =\t%.3f" % struct.unpack('<f', rx_pack[48: 52])[0])
    print("a2 =\t%.3f" % struct.unpack('<f', rx_pack[52: 56])[0])
    print("br_thresh =\t%u" % struct.unpack('<H', rx_pack[56: 58])[0])

    print("sequencer =\t0x%X" % struct.unpack('<H', rx_pack[58: 60])[0])
    print("start_x =\t0x%X" % struct.unpack('<H', rx_pack[60: 62])[0])
    print("start_y =\t0x%X" % struct.unpack('<H', rx_pack[62: 64])[0])
    print("nb_pix =\t0x%X" % struct.unpack('<H', rx_pack[64: 66])[0])
    print("res1_length =\t0x%X" % struct.unpack('<H', rx_pack[66: 68])[0])
    print("res2_timer =\t0x%X" % struct.unpack('<H', rx_pack[68: 70])[0])
    print("res3_timer =\t0x%X" % struct.unpack('<H', rx_pack[70: 72])[0])
    print("ft_timer =\t\t0x%X" % struct.unpack('<H', rx_pack[72: 74])[0])
    print("vcal =\t\t\t0x%X" % struct.unpack('<H', rx_pack[74: 76])[0])
    print("vblack =\t\t0x%X" % struct.unpack('<H', rx_pack[76: 78])[0])
    print("voffset =\t\t0x%X" % struct.unpack('<H', rx_pack[78: 80])[0])
    print("ana_in_adc =\t0x%X" % struct.unpack('<H', rx_pack[80: 82])[0])
    print("pga_setting =\t0x%X" % struct.unpack('<H', rx_pack[82: 84])[0])

def F_angles(x, y):
    """
        Функция расчитывает значения углов по входным данным - центру пятна и коэффициентам калибровки. Возвращает
        два угла: зенитный и азимутальный.
    """
    r = ((x-x0)**2 + (y-y0)**2)**0.5
    zenith = A*r**6 + B*r**5 + C*r**4 + D*r**3 + E*r**2 + F*r

    if (x-x0) > 0:
        azimuth = math.degrees(math.atan((y-y0)/(x-x0))) + 90 + phi0
    else:
        azimuth = math.degrees(math.atan((y-y0)/(x-x0))) + 270 + phi0

    return zenith, azimuth

if __name__ == '__main__':
    main()
    ser.close()
