import smbus2
import time
import json

if __name__ == "__main__":
    from I2Cdev import INA228
else:
    from .I2Cdev import INA228

#親プロセスからのリクエスト
GET_POWER_USE = "get_power_use"
GET_POWER_GEN = "get_power_gen"

#I2Cアドレス
POWER_USE_ADDR = 0x4a
POWER_GEN_ADDR = 0x45

#I2Cバスの設定
bus = smbus2.SMBus(1)  # I2C-1 を使用

#電源関係
Power_use = INA228.INA228(bus, POWER_USE_ADDR)
Power_gen = INA228.INA228(bus, POWER_GEN_ADDR)
def get_power_info(dev):
    return {
        "Voltage [V]": dev.get_vbus_voltage(),
        "Current [A]": dev.get_current(),
        "Power [W]": dev.get_power()
    }


if __name__ == "__main__":
    print("I2C.py is running.")
    #データの受け皿
    payload = {}

    while True:

        payload["Power_use"] = get_power_info(Power_use)
        payload["Power_gen"] = get_power_info(Power_gen)
        print(payload)
        time.sleep(1)

