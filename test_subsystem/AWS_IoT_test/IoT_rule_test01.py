import json
import time
import paho.mqtt.client as mqtt

# jsonファイルを読み込み
with open("../../private/private.json", "r") as f:
    config = json.load(f)

print(config)
print(config["AWS"]["IoT_Endpoint"])

# AWS IoT のエンドポイントとトピック
AWS_IOT_ENDPOINT = config["AWS"]["IoT_Endpoint"]

MQTT_TOPIC = "test01/data"

# MQTT クライアントの設定
client = mqtt.Client(client_id="Dev-001", clean_session=False)
#client.tls_set("AmazonRootCA1.pem", "certificate.pem.crt", "private.pem.key")

root_CA = config["AWS"]["root_CA"]
crt = config["AWS"]["crt"]
key = config["AWS"]["key"]

client.tls_set(root_CA, crt, key)
print(client.connect(AWS_IOT_ENDPOINT, 8883, 60))

client.loop_start()

# データ送信
while True:
    payload = {
        "device_id": "sensor-001",
        "temperature": 25.6,
        "humidity": 60,
        "timestamp": int(time.time())
    }
    rc, mid = client.publish(MQTT_TOPIC, json.dumps(payload))
    print(rc, ", ", mid)
    print("Data sent:", payload)
    time.sleep(10)
