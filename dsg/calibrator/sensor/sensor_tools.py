import crcmod
import time
import struct
import datetime
import serial
import dsg.calibrator.sensor.sensor_settings as ss
from dsg.calibrator.sensor.sensor_init import SunSensor


class Tools(SunSensor):
    "Class for low level data processing"

    prev_time: datetime = datetime.datetime.now()
    take_photo_cmd: int = 0x04

    # def __init__(self) -> None:
    #     self.sensor: SunSensor = SunSensor()

    def _setGamsettings(self) -> None:
        tmp_buf: str = self._addCrc16([0xAA, ss.lupa300_set['addr_rec'], ss.lupa300_set['addr_send'], 0x00, 0x00, 0x20, 0x09, 0x00,
                    ss.gam_mode, ss.gam_smplrt_div,
                    ss.g_full_scale, ss.g_dlpf_cfg, ss.g_lp_mode_cfg,
                    ss.a_full_scale, ss.a_dec2_cfg, ss.a_dlpf_cfg, ss.m_odr,
                    0, 0])
        self.write(tmp_buf)
        self.prev_time = datetime.datetime.now()
        time.sleep(0.25)
        packet: str = self._addCrc16([0xAA, ss.lupa300_set['addr_rec'], ss.lupa300_set['addr_send'], 0x00, 0x00, 0x11, 0x06, 0x00, ss.emissivity,
                    ss.reflection_temp & 0xFF, ss.reflection_temp >> 8, ss.resolution, ss.ref_rate, ss.mode, 0, 0])
        self.write(packet)
        time.sleep(0.5)

    def _settingsMatrix(self) -> None:
        if ss.lupa300_set['integration_time'] > 479:
            ss.lupa300_set['res1_lenght'] = 4
        else:
            ss.lupa300_set['res1_lenght'] = 484 - ss.lupa300_set['integration_time']
        ss.lupa300_set['ft_timer'] = ss.lupa300_set['res1_lenght'] + ss.lupa300_set['integration_time']

        self.write(
            self._addCrc16([0xAA, ss.lupa300_set['addr_rec'], ss.lupa300_set['addr_send'], 0x00, 0x00, 0x01, 0x09, 0x00, ss.lupa300_set['res1_lenght'] & 0xFF,
                    ss.lupa300_set['res1_lenght'] >> 8, ss.lupa300_set['ft_timer'] & 0xFF, ss.lupa300_set['ft_timer'] >> 8, ss.lupa300_set['vcal'], ss.lupa300_set['vblack'],
                    ss.lupa300_set['voffset'], ss.lupa300_set['pga_setting'] & 0xFF, ss.lupa300_set['pga_setting'] >> 8, 0x00, 0x00]))
        self.write(
            self._addCrc16([0xAA, ss.lupa300_set['addr_rec'], ss.lupa300_set['addr_send'], 0x00, 0x00, 0x0C, 0x01, 0x00, ss.lupa300_set['black_level'], 0, 0]))

    def _addCrc16(self, check_list: list[bytes]) -> str:
        crc16_fun = crcmod.mkCrcFun(0x18005, 0xFFFF)
        crc_word = crc16_fun(serial.to_bytes(check_list[:-2]))
        check_list[-2] = crc_word & 0x00FF
        check_list[-1] = crc_word >> 8
        return check_list

    def _packVerification(self, set, packet) -> int:
        if len(packet) == 0:
            print("WARNING. Packet is absent.")
            return 1
        if packet[0] != 0xAA:
            print("WARNING. Packet preambula is absent.")
            return 1
        if packet[1] != set['addr_send']:
            print("WARNING. Received address is wrong.")
            return 1

        num_byte: bytes = packet[7] << 8 | packet[6]
        if (num_byte + 10) != len(packet):
            print("WARNING. Packet size is too large. num_bytes = %d" % num_byte)
            return 1

        crc_pack: bytes = packet[8 + num_byte + 1] << 8 | packet[8 + num_byte]
        crc16_fun: any = crcmod.mkCrcFun(0x18005, 0xFFFF)
        crc_word: any = crc16_fun(serial.to_bytes(packet[:-2]))

        if crc_pack != crc_word:
            print("WARNING. Received CRC16 is wrong.")
            return 1
        return 0

    def getImg10bit(self) -> tuple[float, float, float, float]:
        while True:
            self._setGamsettings()
            self._settingsMatrix()
            time.sleep(0.1)
            self.read_timeout = 3
            self.flush()
            self.write(self._addCrc16([0xAA, ss.lupa300_set['addr_rec'], ss.lupa300_set['addr_send'],
                                0x00, 0x00, self.take_photo_cmd, 0x08, 0x00,
                                ss.test_center_x & 0x00FF, ss.test_center_x >> 8,
                                ss.test_center_y & 0x00FF, ss.test_center_y >> 8,
                                ss.bg_noise & 0x00FF, ss.bg_noise >> 8,
                                ss.salt_noise & 0x00FF, ss.salt_noise >> 8, 0x00, 0x00]))

            rx_buf: bytes = self.read(30)
            if not self._packVerification(ss.lupa300_set, rx_buf):
                if rx_buf[8:13] != b'ERROR':
                    x_sens = struct.unpack(   '<f', rx_buf[8:12])[0]
                    y_sens = struct.unpack(   '<f', rx_buf[12:16])[0]
                    zen_sens = struct.unpack( '<f', rx_buf[16:20])[0]
                    azim_sens = struct.unpack('<f', rx_buf[20:24])[0]
                    result: tuple = (x_sens, y_sens, zen_sens, azim_sens)
                    if x_sens != 0.0 and y_sens != 0.0:
                        break
        self.read_timeout = 0.1
        return result

    def set_calib_coeff(self, coeff_arr: list) -> None:
        tx_pack: list = [0xAA, ss.lupa300_set['addr_rec'], ss.lupa300_set['addr_send'], 0x00, 0x00, 0x0D, 48, 0]

        for element in coeff_arr:
            tx_pack += struct.pack('<f', element)

        tx_pack += [0, 0]
        self.write(self._addCrc16(tx_pack))
        time.sleep(3)

    def get_calib_coeff(self) -> None:
        """
            Функция запрашивает у датчика его данные калибровки и выводит их в консоль.
        """
        # проверка записанных переменных
        time.sleep(0.1)
        self.read_timeout = 1
        self.flush()
        self.write(self._addCrc16([0xAA, ss.lupa300_set['addr_rec'], ss.lupa300_set['addr_send'], 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00, 0x00]))
        rx_pack = self.read(90)

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

if __name__ == "__main__":
    tool: Tools = Tools()
    coefs: list = [
        -2.1003e-01, 4.1407e-01, -7.7395e-04, 7.9406e-06, -1.0717e-07, 5.4699e-10, -9.8182e-13,
        235.23075, 249.04875, 0.0,
        1.0, 3.0
        ]
    tool.connect()
    tool._settingsMatrix()
    tool.set_calib_coeff(coefs)
    tool._settingsMatrix()
    tool.get_calib_coeff()
