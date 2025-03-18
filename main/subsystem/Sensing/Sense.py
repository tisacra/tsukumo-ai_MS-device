from . import I2Cbus
from . import soil_sensor
import json

#親プロセスからのリクエスト
GET_SOIL_INFO = "get_soil_info"

def Sensing(conn, start_event):
    soil_sensor.setup()
    start_event.wait()
    while True:
        request = conn.recv()
        payload = {}
        if request == I2Cbus.GET_POWER_USE:
            payload["Power_use"] = I2Cbus.get_power_info(I2Cbus.Power_use)
            conn.send(payload)
        elif request == I2Cbus.GET_POWER_GEN:
            payload["Power_gen"] = I2Cbus.get_power_info(I2Cbus.Power_gen)
            conn.send(payload)
        elif request == GET_SOIL_INFO:
            payload["Soil_info"] = soil_sensor.get_soil_info()
            conn.send(payload)
        else:
            pass