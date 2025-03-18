import json
import signal
import time
from multiprocessing import Process, Event, Queue

import subsystem.MQTT as MQTT

project_dir = "../"
log_interval = 3

#mqtt通信の準備
MQTT.setup_mqtt(project_dir)
MQTT_TOPIC = "test01/data"

#データ骨子の読み込み
with open("packet_frame.json", "r") as f:
    p_frame = json.load(f)

#イベント、キューの準備
start_event = Event()
flush_request = Event()

#サブシステムの起動


#定期処理用タイマを設定
def scheduler(arg1, arg2):
    #集計などの処理




    MQTT.mqtt_send(MQTT_TOPIC, p_frame)


signal.signal(signal.SIGALRM, scheduler)
signal.setitimer(signal.ITIMER_REAL, 1, log_interval)

while True:
    pass