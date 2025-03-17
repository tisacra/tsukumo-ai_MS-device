import smbus2
import time

# I2C バスの設定
I2C_ADDR = 0x4a  # センサの I2C アドレス+

VBUS_ADDR = 0x05  # バス電圧のレジスタアドレス

bus = smbus2.SMBus(1)  # I2C-1 を使用

def __convert2comp2float(twocompdata, nrofbit, factor):

        isnegative = 1
        isnegative = (isnegative << (nrofbit - 1))

        dietemp = twocompdata

        if(dietemp > isnegative):
            dietemp = (dietemp - (2*isnegative)) * factor
        else:
            dietemp = (dietemp * factor)

        return dietemp

def read_register24(addr, register):

        result = bus.read_i2c_block_data(addr, register, 3)
        
        register_value = ((result[0] << 16) & 0xFF0000) | ((result[1] << 8) & 0xFF00) | (result[2] & 0xFF)

        #print("Read register 24 bits - 0x%02X: 0x%05X = 0b%s" %(register, register_value, self.__binary_as_string(register_value)))

        return register_value

def read_BusVoltage():
    raw = read_register24(I2C_ADDR, VBUS_ADDR) # 電圧測定コマンド
    conversion_factor =  0.1953125 * 1e-3  # 補正 [V]
    VBUS = __convert2comp2float(raw >> 4, 20, conversion_factor)
    return VBUS

print(f"Voltage: {read_BusVoltage():.2f} [V]")