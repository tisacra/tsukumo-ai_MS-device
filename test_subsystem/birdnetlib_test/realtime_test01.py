#birdnet
from birdnetlib import RecordingBuffer
from birdnetlib.analyzer import Analyzer
#pyaudio
import pyaudio
import numpy as np


#録音の設定
bit_depth = 16
#CHUNK = int(w/2) * int(bit_depth/8)
sam_rate = 48000
sam_sec = 3 # analyzeのmin_lenが1.5なので、4秒以上にしたい
BUF = int(sam_rate*sam_sec)
CHUNK = int(BUF/2)
p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16,     #データの型
                channels=1,     #ステレオかモノラルかの選択 1でモノラル 2でステレオ
                rate=sam_rate,      #サンプリングレート
                input=True,
                input_device_index = 4,     #マイクの指定
                frames_per_buffer=BUF)    #データ数

# Load and initialize the BirdNET-Analyzer models.
analyzer = Analyzer()

while(1):
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
        min_conf=0.25,
    )
    recording.analyze()
    print(recording.detections)

    stream.start_stream()
