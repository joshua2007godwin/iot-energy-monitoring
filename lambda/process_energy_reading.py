import json, os, time
import boto3
from decimal import Decimal

table = boto3.resource("dynamodb").Table("EnergyReadings")
sns = boto3.client("sns")
TOPIC = os.environ.get("SNS_TOPIC_ARN")
TARIFF = 8.0  # Rs per kWh

def lambda_handler(event, context):
    v = float(event["voltage"])
    i = float(event["current"])
    pf = float(event["pf"])
    kwh = float(event["kwh"])

    power_kw = round(v * i * pf / 1000, 3)
    cost = round(kwh * TARIFF, 2)

    alerts = []
    if v > 250: alerts.append("OVERVOLTAGE")
    if v < 200: alerts.append("UNDERVOLTAGE")
    if i > 20: alerts.append("OVERLOAD")
    if pf < 0.85: alerts.append("LOW_PF")

    item = {
        "deviceId": event["deviceId"],
        "timestamp": int(event.get("timestamp", time.time() * 1000)),
        "voltage": v, "current": i, "pf": pf,
        "power_kw": power_kw, "kwh": kwh, "cost": cost,
        "alerts": alerts,
    }
    table.put_item(Item=json.loads(json.dumps(item), parse_float=Decimal))

    if alerts and TOPIC:
        sns.publish(TopicArn=TOPIC,
                    Subject=f"Energy alert: {event['deviceId']}",
                    Message=json.dumps(item))
    return item