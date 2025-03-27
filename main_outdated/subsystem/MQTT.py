import json
import time
import datetime
import paho.mqtt.client as mqtt


client = None

def setup_mqtt(project_dir):
    global client

    with open(project_dir + "private/private.json", "r") as f:
        config = json.load(f)

    # MQTT クライアントの設定
    client = mqtt.Client(client_id=config["Device"]["ID"], clean_session=False)

    # AWS IoT のエンドポイントとトピック
    AWS_IOT_ENDPOINT = config["AWS"]["IoT_Endpoint"]

    root_CA = project_dir + config["AWS"]["root_CA"]
    crt = project_dir + config["AWS"]["crt"]
    key = project_dir + config["AWS"]["key"]
    client.tls_set(root_CA, crt, key)

    print(client.connect(AWS_IOT_ENDPOINT, 8883, 60))

    client.loop_start()

# データ送信
def mqtt_send(mqtt_topic, payload):
    payload["timestamp"] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')
    rc, mid = client.publish(mqtt_topic, json.dumps(payload))
    #print(rc, ", ", mid)
    #print("Data sent:", payload)
    pass


if __name__ == "__main__":
    print("MQTT.py is running.")

    MQTT_TOPIC = "test01/data"
    project_dir = "../../"
    setup_mqtt(project_dir)

    while True:
        now = datetime.datetime.fromtimestamp(time.time())
        payload = {
            "temperature": 25.6,
            "humidity": 60,
            "timestamp": now.strftime('%Y%m%d_%H%M%S')
        }
        mqtt_send(MQTT_TOPIC, payload)
        time.sleep(10)