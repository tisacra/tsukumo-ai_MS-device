import serial
import time

port = '/dev/ttyAMA2'
bps = 115200
timeout = 1

def GNSS_setup():
    global ser
    try:
        ser = serial.Serial(port, bps, timeout=timeout)

    except Exception as e:
        print("エラー:", e)
        return None
    # ※ 必要に応じて、GNSS機能を有効にするコマンドを送信する場合があります
    ser.write("AT+UGPS=1,1,1\r\n".encode())
    time.sleep(2)  # GNSS起動後、位置情報が取得可能になるまで待機
    ser.write("AT+UGGGA=1\r\n".encode())
    time.sleep(2)  # GNSS起動後、位置情報が取得可能になるまで待機

def get_GNSS_info():
    """
    指定のシリアルポートを通して、GNSS情報取得用のATコマンドを送信し、その応答を返す関数。
    
    port      : シリアルポート（例: '/dev/ttyUSB0' または 'COM3'）
    baudrate  : 通信速度（一般的に115200bpsなど）
    timeout   : 応答待ちタイムアウト（秒）
    """

    # GNSS情報取得用の AT コマンドを送信（例：AT+UGNSINF）
    cmd = "AT+UGGGA?\r\n"
    ser.write(cmd.encode())
    time.sleep(1)  # 応答が返ってくるまで待機
    
    # シリアルポートから受信した全データを読み出す
    response = ser.read_all().decode(errors='ignore')
    return response
    

if __name__ == '__main__':
    GNSS_setup()
    gnss_data = get_GNSS_info()
    if gnss_data:
        print("取得した GNSS 情報:")
        print(gnss_data)
    else:
        print("GNSS 情報の取得に失敗しました。")
