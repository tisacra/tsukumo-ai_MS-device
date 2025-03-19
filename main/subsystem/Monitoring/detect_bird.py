#birdnet
from birdnetlib import RecordingBuffer
from birdnetlib.analyzer import Analyzer
#pyaudio
import pyaudio
import numpy as np
import copy
import signal

#親プロセスからのリクエストを受け取る
GET_ACCUMULATIVE_REC = "get_accumulative_rec"
accumulative_rec = {}

#録音の設定
bit_depth = 16
#CHUNK = int(w/2) * int(bit_depth/8)
sam_rate = 48000
sam_sec = 3 # analyzeのmin_lenが1.5なので、4秒以上にしたい
BUF = int(sam_rate*sam_sec)
CHUNK = int(BUF/2)


# Load and initialize the BirdNET-Analyzer models.
analyzer = None
stream = None

def setup():
    global analyzer, stream
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,     #データの型
                    channels=1,     #ステレオかモノラルかの選択 1でモノラル 2でステレオ
                    rate=sam_rate,      #サンプリングレート
                    input=True,
                    input_device_index = 4,     #マイクの指定
                    frames_per_buffer=BUF)    #データ数

    if analyzer is None:
        analyzer = Analyzer()


def get_bird_record(arg1=None, arg2=None):
    global accumulative_rec
    print("get_bird_record called. :", accumulative_rec)
    tmp = accumulative_rec
    #accumulative_rec = {}
    flash()
    return tmp

def flash():
    global accumulative_rec
    accumulative_rec = {}
    pass

def accumulation(list):
    global accumulative_rec
    if list is []:
        pass
    else:
        for rec in list:
            if rec["common_name"] not in accumulative_rec:
                accumulative_rec[rec["common_name"]] = rec["confidence"]
            else:
                accumulative_rec[rec["common_name"]] += rec["confidence"]

def start_analyze(conn = None, start_event = None):
    if start_event is not None:
        print("birdNET analyze waiting...")
        start_event.wait()
    print("birdNET analyze start.")
    
    while True:
        if conn is not None:
            request = conn.recv()
            if request == GET_ACCUMULATIVE_REC:
                conn.send(accumulative_rec)
                flash()
            else:
                pass


        data_buf = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False) ,dtype="int16")   #CHUNKだけデータを読み込む
        #print(data_buf)
        #print(len(data_buf))
        stream.stop_stream()    #推論中は録音停止

        recording = RecordingBuffer(
            analyzer,
            data_buf,
            sam_rate,
            #lat=-1,
            #lon=-1,
            #date=datetime(year=2024, month=5, day=10), # use date or week_48
            min_conf=0.10,
        )
        recording.analyze()
        #print(recording.detections)
        accumulation(recording.detections)
        #print("accumulative_rec : ", accumulative_rec)
        stream.start_stream()

if __name__ == "__main__":
    print("detect_bird.py is running.")

    signal.signal(signal.SIGALRM, get_bird_record)
    signal.setitimer(signal.ITIMER_REAL, 5, 10)
    setup()
    start_analyze()