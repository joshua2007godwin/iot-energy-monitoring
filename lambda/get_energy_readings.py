import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

table = boto3.resource("dynamodb").Table("EnergyReadings")

def conv(o):
    if isinstance(o, Decimal):
        return float(o)
    raise TypeError

def lambda_handler(event, context):
    p = event.get("queryStringParameters") or {}
    device = p.get("deviceId", "meter-01")
    limit = min(int(p.get("limit", 50)), 200)
    res = table.query(
        KeyConditionExpression=Key("deviceId").eq(device),
        ScanIndexForward=False,
        Limit=limit,
    )
    items = list(reversed(res["Items"]))
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(items, default=conv),
    }