import json
import signal
import time
from multiprocessing import Process, Event, Queue, Pipe

import subsystem.MQTT as MQTT
import subsystem.Sensing.Sense as Sense
import subsystem.Sensing.I2Cbus as I2Cbus

project_dir = "../"
log_interval = 3 #[s]

#mqtt通信の準備
MQTT.setup_mqtt(project_dir)
MQTT_TOPIC = "test01/data"

#データ骨子の読み込み
with open("packet_frame.json", "r") as f:
    p_frame = json.load(f)

#イベント、キューの準備
start_event = Event()
flush_request = Event()

#パイプの準備
Sense_parent_conn, Sense_child_conn = Pipe()

#サブシステムの起動
p_Sense = Process(target=Sense.Sensing, args=(Sense_child_conn, start_event))
p_Sense.daemon = True
p_Sense.start()


#定期処理用タイマを設定
def scheduler(arg1, arg2):
    #集計などの処理

    #センシングデータの取得
    Sense_parent_conn.send(I2Cbus.GET_POWER_USE)
    data = Sense_parent_conn.recv()

    p_frame["Sensor"] = data

    print("Data sent:", p_frame)
    MQTT.mqtt_send(MQTT_TOPIC, p_frame)

#メインループ開始
print("Main.py is running.")
start_event.set()

signal.signal(signal.SIGALRM, scheduler)
signal.setitimer(signal.ITIMER_REAL, 1, log_interval)

while True:
    pass