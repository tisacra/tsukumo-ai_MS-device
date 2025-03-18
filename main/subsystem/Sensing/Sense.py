from . import I2Cbus
import json

def Sensing(conn, start_event):
    start_event.wait()
    while True:
        request = conn.recv()
        if request == I2Cbus.GET_POWER_USE:
            payload = {}
            payload["Power_use"] = I2Cbus.get_power_info(I2Cbus.Power_use)
            conn.send(payload)
        else:
            pass