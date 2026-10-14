import json, time, random
from awscrt import mqtt
from awsiot import mqtt_connection_builder

ENDPOINT = "your-endpoint-ats.iot.us-east-1.amazonaws.com"DEVICE_ID = "meter-01"
TOPIC = f"energy/{DEVICE_ID}/data"

conn = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath="certs/device.pem.crt",
    pri_key_filepath="certs/private.pem.key",
    ca_filepath="certs/AmazonRootCA1.pem",
    client_id=DEVICE_ID,
    keep_alive_secs=30,
)
conn.connect().result()
print("Connected to AWS IoT")

kwh = 0.0
while True:
    v = random.gauss(230, 3)
    i = random.uniform(5, 15)
    pf = random.uniform(0.88, 0.98)

    # inject faults ~20% of the time
    r = random.random()
    if r < 0.08:
        v = random.choice([random.uniform(255, 270), random.uniform(180, 198)])
    elif r < 0.14:
        i = random.uniform(21, 28)
    elif r < 0.20:
        pf = random.uniform(0.6, 0.8)

    power_kw = v * i * pf / 1000
    kwh += power_kw * 0.1  # each reading represents 6 min of usage

    msg = {
        "deviceId": DEVICE_ID,
        "timestamp": int(time.time() * 1000),
        "voltage": round(v, 1),
        "current": round(i, 2),
        "pf": round(pf, 2),
        "kwh": round(kwh, 3),
    }
    conn.publish(topic=TOPIC, payload=json.dumps(msg),
                 qos=mqtt.QoS.AT_LEAST_ONCE)[0].result()
    print("sent", msg)
    time.sleep(5)