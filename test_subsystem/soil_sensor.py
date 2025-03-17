import serial
import time

#port = "COM10" 
port = "/dev/ttyUSB0"

Com = [0x01, 0x03, 0x00, 0x00, 0x00, 0x04, 0x44, 0x09]
tem, hum, ph = 0.0, 0.0, 0.0
ec = 0

tem_low_th = 0.
tem_high_th = 20.

def tem_map(x):
    if x < tem_low_th:
        return 0
    elif x > tem_low_th and x < tem_high_th:
        return 1
    else:
        return 2

def setup():
    global ser
    ser = serial.Serial(port, 9600, timeout=1)
    if ser.is_open:
        print(f"Serial port {port} is open.")
    else:
        print(f"Serial port {port} is not open.")
        setup()

def readHumitureECPH():
    global tem, hum, ec, ph
    flag = True
    Data = [0] * 13
    while flag:
        time.sleep(0.1)
        ser.write(bytearray(Com))
        time.sleep(0.01)
        if ser.in_waiting > 0:
            ch = ser.read(1)
            if ch == b'\x01':
                Data[0] = 1
                if ser.in_waiting > 0:
                    ch = ser.read(1)
                    if ch == b'\x03':
                        Data[1] = 3
                        if ser.in_waiting > 0:
                            ch = ser.read(1)
                            if ch == b'\x08':
                                Data[2] = 8
                                if ser.in_waiting >= 10:
                                    Data[3:13] = ser.read(10)
                                    if CRC16_2(Data[:11]) == (Data[11] * 256 + Data[12]):
                                        hum = (Data[3] * 256 + Data[4]) / 10.0
                                        tem = (Data[5] * 256 + Data[6]) / 10.0
                                        ec = Data[7] * 256 + Data[8]
                                        ph = (Data[9] * 256 + Data[10]) / 10.0
                                        flag = False
        ser.reset_input_buffer()

def CRC16_2(buf):
    crc = 0xFFFF
    for pos in buf:
        crc ^= pos
        for i in range(8):
            if (crc & 1):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return ((crc & 0xFF) << 8) | ((crc >> 8) & 0xFF)

def loop():
    while True:
        readHumitureECPH()
        #print(f"TEM = {tem:.1f} °C  HUM = {hum:.1f} %RH  EC = {ec} us/cm  PH = {ph:.1f}")
        print(f"TEM = {tem:.1f} °C ({tem_map(tem)}) HUM = {hum:.1f} %RH  EC = {ec} us/cm  PH = {ph:.1f}")
        time.sleep(1)

if __name__ == "__main__":
    setup()
    loop()
