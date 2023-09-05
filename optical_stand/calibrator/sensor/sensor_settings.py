lupa300_set: dict[str, int] = { 'addr_rec'          : 0x01,         #адрес датчика которому адресована команда
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

test_center_x = 300
test_center_y = 300
bg_noise = 0
salt_noise = 0

emissivity = 97             # в %
reflection_temp = 2301      # в сотых долях градуса (2301 == 23.01С)
resolution = 3              # 0 - 16bit, 1 - 17bit, 2 - 18bit, 3 - 19bit
ref_rate = 3                # 0 - 0.5 Гц, 1 - 1 Гц, 2 - 2 Гц, 3 - 4 Гц, 4 - 8 Гц, 5 - 16 Гц, 6 - 32 Гц, 7 - 64 Гц
mode = 1                    # 0 - выключение между измерениями, 1 - постоянно включен

gam_mode = 3
gam_smplrt_div = 9
g_full_scale = 3
g_dlpf_cfg = 3
g_lp_mode_cfg = 0
a_full_scale = 0
a_dec2_cfg = 0
a_dlpf_cfg = 3
m_odr = 1
