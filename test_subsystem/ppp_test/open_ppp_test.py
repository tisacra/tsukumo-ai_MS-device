import serial
import sys

def open_ppp():
    try:
        # シリアルポートを 115200 baud でオープン
        ser = serial.Serial('/dev/ttyAMA3', 115200, timeout=1)
        print("シリアルポートに接続しました: /dev/ttyAMA3 @ 115200 baud")
    except Exception as e:
        print("シリアルポートのオープンに失敗しました:", e)
        sys.exit(1)