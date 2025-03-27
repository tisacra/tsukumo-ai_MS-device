import serial
import json
import time
import datetime

debug = True

# シリアルポートの設定（使用するポートとボーレートは環境に合わせて変更してください）
ser = None
SERIAL_PORT = '/dev/ttyAMA2'
BAUD_RATE = 460800

keepalive = 60

MQTT_TOPIC = "test02"

APN = '"soracom.io"'

project_dir = "../"
#データ骨子の読み込み
with open(project_dir + "private/private.json", "r") as f:
        config = json.load(f)

def send_at_command(ser, command, wait_for="OK", timeout=10):
    """
    シリアルポートに AT コマンドを送信し、指定の文字列がレスポンスに含まれるまで待機する。
    """
    full_command = command + "\r"
    ser.write(full_command.encode())
    if debug is True:
        print("送信: ", command)
    
    end_time = time.time() + timeout
    response = ""
    while time.time() < end_time:
        if ser.in_waiting:
            resp = ser.read(ser.in_waiting).decode(errors="ignore")
            response += resp
            # 指定の文字列が含まれていれば終了
            if wait_for in response:
                break
        time.sleep(0.1)

    if debug is True:
        print("受信: ", response)
    return response

def import_tls_file(ser, type, content, file_name):
    # AT+USECMNGコマンドの作成（例：インポートモード0、パラメータ0）
    at_command = 'AT+USECMNG=0,{},"{}",{}'.format(type, file_name, len(content))
    print("送信コマンド:", at_command.encode())
    ser.write((at_command + "\r\n").encode())

    # モジュールからの応答（プロンプト「>」）待機
    time.sleep(1)
    response = ser.read(ser.in_waiting or 1).decode('utf-8', errors='ignore')
    print("初回応答:", response)
    if ">" not in response:
        print("データ入力プロンプトが受信できませんでした。")
        ser.close()
        return

    # 証明書データの送信
    print("証明書データを送信します（サイズ：{}バイト）".format(len(content)))
    ser.write(content.encode())
    # 場合によっては、データ送信完了を示すCtrl+Z (0x1A) を送信する（プロトコルに依存）
    #ser.write(b'\r')

    # 応答を待機
    time.sleep(10)
    final_response = ser.read(ser.in_waiting or 1).decode('utf-8', errors='ignore')
    print("最終応答:", final_response)

def import_tls_files(ser):
    # TLS認証の有効化および証明書設定
    # 以下の例では、enable_flag=1, option=2 とし、証明書ファイルパスを指定しています。
    # 証明書ファイルは、事前にモジュールのファイルシステムにアップロードしておく必要があります。
    root_CA = project_dir + config["AWS"]["root_CA"]
    root_CA_data = open(root_CA).read()
    crt = project_dir + config["AWS"]["crt"]
    crt_data = open(crt).read()
    key = project_dir + config["AWS"]["key"]
    key_data = open(key).read()

    #send_at_command(ser, 'AT+USECMNG=0,0,"rootCA",1133\n\r'+str_root_CA, timeout=120)
    import_tls_file(ser, 0, root_CA_data, "rootCA")
    import_tls_file(ser, 1, crt_data, "crt")
    import_tls_file(ser, 2, key_data, "key")
    #send_at_command(ser, "AT+USECMNG=3")

def setup():
    global ser
    print("start SARA-R5 setup...")
    # シリアルポートのオープン
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # モジュール起動待ち
    except Exception as e:
        print("シリアルポートのオープンに失敗:", e)
        return

    send_at_command(ser, "AT+CMEE=1", timeout=60)
    
    #NTT向け設定のインポート
    if True:
        send_at_command(ser, "AT+CFUN=0")
        send_at_command(ser, "AT+UMNOPROF=20")
        send_at_command(ser, "AT+CFUN=16", timeout=60)
        time.sleep(5)
        if debug is True:
            send_at_command(ser, "AT+UMNOPROF?", timeout=30)

    if True:
        send_at_command(ser, "AT+CFUN=0")
        send_at_command(ser, "AT+CGDCONT=1,\"IPV4V6\",\"soracom.io\"")
        send_at_command(ser, "AT+CFUN=1")

    while True:
        res = send_at_command(ser, "AT+COPS?")
        if "docomo" in res:
            print(" - SARA-R5 is connected to the NTT network.")
            break
        if False:
            if True:
                pass
            else:
                print(" - SARA-R5 is not connected to the network.")
                exit(-1)

    if debug is True:
        send_at_command(ser, "AT+CGDCONT?")

    send_at_command(ser, "AT+UPSD=1,0,0")
    send_at_command(ser, "AT+UPSD=1,100,1")
    send_at_command(ser, "AT+UPSDA=1,3",wait_for="+UUPSDA:", timeout=60)

    #USERCPRF_profileは0を使用
    send_at_command(ser, 'AT+USECPRF=0,3,"rootCA"')
    send_at_command(ser, 'AT+USECPRF=0,5,"crt"')
    send_at_command(ser, 'AT+USECPRF=0,6,"key"')

    #send_at_command(ser, 'AT+UMQTT?')

    if False:
        
        
        send_at_command(ser, 'AT+UMQTT=11,1,0')

        # 1. MQTT プロフィールの設定
        # MQTT クライアント ID の設定（例：MyClientID）
        send_at_command(ser, 'AT+UMQTT=0,"'+config["Device"]["ID"]+'"')
        # MQTT サーバー（ブローカー）の指定（ドメイン名の場合）
        send_at_command(ser, 'AT+UMQTT=2,"'+config["AWS"]["IoT_Endpoint"]+'"')
        # キープアライブ等のパラメータ設定（例：keepalive 3600秒、linger 20秒）
        send_at_command(ser, "AT+UMQTT=10,"+str(keepalive)+",20")

        
        # 2. プロフィールの保存（リセット後も設定を保持する場合）
        send_at_command(ser, "AT+UMQTTNV=2")
    else:
        send_at_command(ser, 'AT+UMQTTNV=1')
    
    #ネットワーク状況確認
    if debug is True:
        send_at_command(ser, "AT+CGREG?")
        send_at_command(ser, "AT+CGDCONT?")
        send_at_command(ser, "AT+CGACT?")

    # 3. MQTT サーバーへの接続開始
    # 接続要求を送信し、接続成功時の URC (+UUMQTTC: 1,1 など) を待機
    while True:
        res = send_at_command(ser, "AT+UMQTTC=1", wait_for="+UUMQTTC:", timeout=60)
        print(res)
                
        send_at_command(ser, "AT+UMQTTER", timeout=60)
        if " 1,1\r" in res:
            break

    print(" - SARA-R5 setup done.")

def MQTT_send(topic, message):
    message["timestamp"] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')
    if debug is True:
        print(len(json.dumps(message)))
    tmp = json.dumps(message)
    print(tmp)
    send_message(topic, tmp)

def send_message(topic, message):
    global ser
    res = send_at_command(ser, 'AT+UMQTTC=2,0,0,0,"{}","{}"'.format(topic, message))
    if "ERROR" in res:
        print(" - Failed to send message.")
        res = send_at_command(ser, "AT+UMQTTER", timeout=60)
        print(res)


def GNSS_setup():
    global ser
    print("start GNSS setup...")
    send_at_command(ser, "AT+CFUN=1")
    
    # ※ 必要に応じて、GNSS機能を有効にするコマンドを送信する場合があります
    send_at_command(ser, "AT+UGPS=1,1,1")
    time.sleep(2)  # GNSS起動後、位置情報が取得可能になるまで待機
    send_at_command(ser, "AT+UGGGA=1")
    time.sleep(2)  # GNSS起動後、位置情報が取得可能になるまで待機

    print(" - GNSS setup done.")

def get_GNSS_info():
    # GNSS情報取得用の AT コマンドを送信（例：AT+UGNSINF）
    response = send_at_command(ser, "AT+UGGGA?")
    tmp = response.split(':')[1]
    data = tmp.split('\n')

    print("GNSS info:", data)
    return data[0].replace("\r", "")

def main():
    # 4. パブリッシュ（メッセージ送信）の例
    # トピック "sensor/temperature" に "25.5°C" を送信（QoS 0, retain 0）
    send_message(MQTT_TOPIC, "25.5°C")
    send_at_command(ser, "AT+UMQTTER", timeout=60)
    
    # 5. サブスクライブ（購読）の例
    # トピックフィルタ "sensor/temperature/#" を購読（最大 QoS 0）
    send_at_command(ser, 'AT+UMQTTC=4,0,"sensor/temperature/#"')
    
    # 6. 受信メッセージの読み出し（必要に応じて定期的に実行）
    send_at_command(ser, "AT+UMQTTC=6")
    
    # 7. エラー確認（最新の MQTT エラーコード取得）
    send_at_command(ser, "AT+UMQTTER")
    
    # 8. MQTT サーバーからの切断（ログアウト）
    send_at_command(ser, "AT+UMQTTC=0")


    send_at_command(ser, "AT+CFUN=0")
    
    # シリアルポートのクローズ
    ser.close()


if __name__ == "__main__":
    setup()
    GNSS_setup()
    get_GNSS_info()

    main()