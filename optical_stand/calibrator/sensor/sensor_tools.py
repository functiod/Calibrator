import crcmod
import time
import struct
import datetime
import serial
import optical_stand.calibrator.sensor.sensor_settings as ss
from optical_stand.calibrator.sensor.sensor_init import SunSensor


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
        time.sleep(0.1)
        self.read_timeout = 3
        self.flush()
        time.sleep(1)
        self.write(self._addCrc16([0xAA, ss.lupa300_set['addr_rec'], ss.lupa300_set['addr_send'],
                             0x00, 0x00, self.take_photo_cmd, 0x08, 0x00,
                            ss.test_center_x & 0x00FF, ss.test_center_x >> 8,
                            ss.test_center_y & 0x00FF, ss.test_center_y >> 8,
                            ss.bg_noise & 0x00FF, ss.bg_noise >> 8,
                            ss.salt_noise & 0x00FF, ss.salt_noise >> 8, 0x00, 0x00]))

        rx_buf: bytes = self.read(30)

        if self._packVerification(ss.lupa300_set, rx_buf):
            print("WARNING: Angles packet is corrupted.")
        else:
            if rx_buf[8:13] == b'ERROR':
                print("WARNING: SS photo received ERROR.")
                return
            x_sens = struct.unpack(   '<f', rx_buf[8:12])[0]
            y_sens = struct.unpack(   '<f', rx_buf[12:16])[0]
            zen_sens = struct.unpack( '<f', rx_buf[16:20])[0]
            azim_sens = struct.unpack('<f', rx_buf[20:24])[0]
        self.read_timeout = 0.1
        return (x_sens, y_sens, zen_sens, azim_sens)
