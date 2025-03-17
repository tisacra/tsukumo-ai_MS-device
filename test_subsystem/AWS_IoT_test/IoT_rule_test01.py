import json
import time
import paho.mqtt.client as mqtt

# AWS IoT のエンドポイントとトピック
AWS_IOT_ENDPOINT = "a1ksbsp9zvccrn-ats.iot.ap-northeast-1.amazonaws.com"
MQTT_TOPIC = "test01/data"

# MQTT クライアントの設定
client = mqtt.Client(client_id="Dev-001", clean_session=False)
#client.tls_set("AmazonRootCA1.pem", "certificate.pem.crt", "private.pem.key")

root_CA = "../AmazonRootCA1.pem"
crt = "../06c55f27cba59a18900b8873a114763a3defa9a7fe3108e06d70f3ddd29f2808-certificate.pem.crt"
key = "../06c55f27cba59a18900b8873a114763a3defa9a7fe3108e06d70f3ddd29f2808-private.pem.key"

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
