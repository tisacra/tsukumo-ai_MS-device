# https://qiita.com/1219mai0410/items/69d89c1a25846af4992d
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import myFFT

epsilon = 1e-5

#録音の設定
bit_depth = 16
w = 2048
#CHUNK = int(w/2) * int(bit_depth/8)
CHUNK = int(w/2)
BUF = 2*4096
RATE = 48000
p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16,     #データの型
                channels=1,     #ステレオかモノラルかの選択 1でモノラル 2でステレオ
                rate=RATE,      #サンプリングレート
                input=True,
                input_device_index = 4,     #マイクの指定
                frames_per_buffer=BUF)    #データ数

#print(CHUNK)

#print(stream)

hamming = np.hamming(w)

#描画の設定
fig, ax = plt.subplots()    #描画領域の作成
fig.canvas.draw()           #figureの描画
bg = fig.canvas.copy_from_bbox(ax.bbox)     #描画情報を保存
line, = ax.plot([0 for _ in range(w)])  #データがないためCHANKの数だけ0をplot
ax.set_ylim(0, 2**(bit_depth-1))   #yのデータ範囲を設定
ax.set_xlim(0,RATE/2)
freq = np.fft.fftfreq(w, d=float(1/RATE))
#print(freq[1:int(w/2)])
line.set_xdata(freq[2:int(w/2)])   #x軸のデータを設定
#print(len(freq[1:int(w/2)]))
fig.show()   #描画

data_pv = np.zeros(int(w/2))

while True:
    tmp = np.frombuffer(stream.read(CHUNK) ,dtype="int16")   #CHUNKだけデータを読み込む
    data = np.hstack([data_pv, tmp])
    print(len(data))
    #print(len(np.frombuffer(data ,dtype="int16")))
    #line.set_ydata(np.abs(np.fft.rfft(np.frombuffer(data ,dtype="int16")))[1:int(w/2)])
    #line.set_ydata(np.abs(myFFT.FFT(np.frombuffer(data ,dtype="int16")*hamming))[1:int(w/2)])
    line.set_ydata(np.fft.rfft(data*hamming)[2:int(w/2)])  #バイナリデータをnumpy配列に変換
    #print(np.abs(np.fft.fft(np.frombuffer(data ,dtype="int16")))[1:int(w/2)])
    fig.canvas.restore_region(bg)   #保存した描画情報を読み込む
    ax.draw_artist(line)        #データを指定
    fig.canvas.blit(ax.bbox)    #保存した描画情報にデータを加える
    fig.canvas.flush_events()   #描画情報をクリア
    data_pv = tmp
    

stream.stop_stream()   #streamを止める
stream.close()   #streamを閉じる
p.terminate()   #pyaudioを終了
