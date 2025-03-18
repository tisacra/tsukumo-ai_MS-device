import json
import time
import datetime
import paho.mqtt.client as mqtt

# jsonファイルを読み込み
with open("../../private/private.json", "r") as f:
    config = json.load(f)

# AWS IoT のエンドポイントとトピック
AWS_IOT_ENDPOINT = config["AWS"]["IoT_Endpoint"]

MQTT_TOPIC = "test01/data"

# MQTT クライアントの設定
client = mqtt.Client(client_id=config["Device"]["ID"], clean_session=False)

root_CA = config["AWS"]["root_CA"]
crt = config["AWS"]["crt"]
key = config["AWS"]["key"]

#client.tls_set("AmazonRootCA1.pem", "certificate.pem.crt", "private.pem.key")
client.tls_set(root_CA, crt, key)
print(client.connect(AWS_IOT_ENDPOINT, 8883, 60))

client.loop_start()

# データ送信
while True:
    now = datetime.datetime.fromtimestamp(time.time())
    payload = {
        "device_id": config["Device"]["ID"],
        "temperature": 25.6,
        "humidity": 60,
        "timestamp": now.strftime('%Y%m%d_%H%M%S')
    }
    rc, mid = client.publish(MQTT_TOPIC, json.dumps(payload))
    print(rc, ", ", mid)
    print("Data sent:", payload)
    time.sleep(10)
