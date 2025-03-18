import smbus2
import time
import json

import I2Cdev.INA228 as INA228

#I2Cアドレス
POWER_USE_ADDR = 0x4a
POWER_SUPPLY_ADDR = 0x41

#I2Cバスの設定
bus = smbus2.SMBus(1)  # I2C-1 を使用

#電源関係
Power_use = INA228.INA228(bus, POWER_USE_ADDR)
#Power_supply = INA228.INA228(bus, POWER_SUPPLY_ADDR)
def get_power_info(dev):
    return {
        "Voltage": dev.get_vbus_voltage(),
        "Current": dev.get_current(),
        "Power": dev.get_power()
    }


#データの受け皿
payload = {}

while True:

    payload["Power_use"] = get_power_info(Power_use)
    #payload["Power_supply"] = get_power_info(Power_supply)
    print(payload)
    time.sleep(1)

