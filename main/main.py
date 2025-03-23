import json
import signal
import time
from multiprocessing import Process, Event, Queue, Pipe

import subsystem.MQTT as MQTT
import subsystem.SARA_R5 as sara
import subsystem.Sensing.Sense as Sense
import subsystem.Sensing.I2Cbus as I2Cbus
import subsystem.Monitoring.Monitor as Monitor


project_dir = "../"
log_interval = 10 #[s]

# SIGINT受信用のフラグ
terminate_flag = Event()
TERMINATE = "terminate"

def signal_handler(signum, frame, pipe):
    print("[親] SIGINTを検出しました。子プロセスに終了シグナルを送信します")
    pipe.send(TERMINATE)
    # フラグをセットし、メインループを抜けるために使用
    terminate_flag.set()


#SARA-R5を使ったMQTT通信およびGNSSの準備
sara.setup()
sara.GNSS_setup()

#MQTT.setup_mqtt(project_dir)

MQTT_TOPIC = "test01/data"

#データ骨子の読み込み
with open("packet_frame.json", "r") as f:
    p_frame = json.load(f)

#イベント、キューの準備
start_event = Event()
#flush_request = Event()


#パイプの準備
Sense_parent_conn, Sense_child_conn = Pipe()
Monitor_parent_conn, Monitor_child_conn = Pipe()


#サブシステムの起動
processes = []
p_Sense = Process(target=Sense.Sensing, args=(Sense_child_conn, start_event))
processes.append(p_Sense)
p_Monitor = Process(target=Monitor.Monitoring, args=(Monitor_child_conn, start_event))
processes.append(p_Monitor)

for p in processes:
    p.deamon = True
    p.start()

#サブシステムの準備完了待ち
S_flag = 0
M_flag = 0
while True:
    Ssig = Sense_parent_conn.recv()
    Msig = Monitor_parent_conn.recv()
    if Ssig == "S1":
        S_flag = 1
    if Msig == "M1":
        M_flag = 1
    if S_flag == 1 and M_flag == 1:
        break

#定期処理用タイマを設定
def scheduler(arg1, arg2):
    #集計などの処理

    #モニタリングデータの取得
    #Monitor_parent_conn.send(Monitor.GET_BIRD_REC)
    #data = Monitor_parent_conn.recv()
    #p_frame["Monitor"] = data

    #センシングデータの取得
    #Sense_parent_conn.send(Sense.GET_SOIL_INFO)
    #data = Sense_parent_conn.recv()
    #p_frame["Sensor"] = data

    #電力情報の取得
    #Sense_parent_conn.send((I2Cbus.GET_POWER_USE, I2Cbus.GET_POWER_GEN))
    #data = Sense_parent_conn.recv()
    #Sense_parent_conn.send(I2Cbus.GET_POWER_GEN)
    #data2 = Sense_parent_conn.recv()
    #p_frame["Device"]["Power"] = data

    #GNSS情報の取得
    data = sara.get_GNSS_info()
    p_frame["Device"]["GNSS"] = data

    print("Data sent:", p_frame)
    #MQTT.mqtt_send(MQTT_TOPIC, p_frame)
    sara.send_message(MQTT_TOPIC, p_frame)


#メインループ開始
print("Main.py is running.")

signal.signal(signal.SIGALRM, scheduler)
signal.setitimer(signal.ITIMER_REAL, 5, log_interval)

# 親プロセスでのSIGINTハンドラの設定（lambdaでpipeを渡す）
signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, Sense_parent_conn))
signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, Monitor_parent_conn))

print("[親] 親プロセスのメインループ開始。Ctrl+Cで終了シグナルを送ります。")

print("subsystems start.")
start_event.set()

try:
    while not terminate_flag.is_set():
        # 親プロセスのメイン処理（例: ループ内で何かの作業）
        pass

finally:
    print("[親] 親プロセス: 子プロセスの終了を待機します")
    for p in processes:
        p.join()
    print("[親] 全ての処理が終了しました")