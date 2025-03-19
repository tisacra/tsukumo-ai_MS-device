from . import I2Cbus
from . import soil_sensor
import json

#親プロセスからのリクエスト
GET_SOIL_INFO = "get_soil_info"


def Sensing(conn, start_event):
    #soil_sensor.setup()

    print("Sensing system is ready...")
    conn.send("S1")
    start_event.wait()

    print("Sensing system start.")

    while True:
        request = conn.recv()
        #print(request)
        payload = {}
        if I2Cbus.GET_POWER_USE in request:
            payload["Power_use"] = I2Cbus.get_power_info(I2Cbus.Power_use)
            #print(payload)
        if I2Cbus.GET_POWER_GEN in request:
            payload["Power_gen"] = I2Cbus.get_power_info(I2Cbus.Power_gen)
            #print(payload)
        if GET_SOIL_INFO in request:
            payload["Soil_info"] = soil_sensor.get_soil_info()
        
        conn.send(payload)