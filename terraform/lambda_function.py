import boto3
import hashlib
import time
import os
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

TTL_DURATION = 3600  # 1 hour in seconds

def lambda_handler(event, context):
    ip = event.get("requestContext", {}).get("http", {}).get("sourceIp", "unknown")


    if not ip:
        return {
            "statusCode": 400,
            "headers": { "Access-Control-Allow-Origin": "*" },
            "body": json.dumps({ "error": "IP address not found" })
        }

    hashed_ip = hashlib.sha256(ip.encode()).hexdigest()
    ip_hashed_key = f"IP#{hashed_ip}"
    counter_key = "COUNTER#global"
    

    try:
        response = table.get_item(Key={"ip": ip_hashed_key})

        if "Item" not in response:
            ttl = int(time.time()) + TTL_DURATION
            table.put_item(Item={"ip": ip_hashed_key, "ttl": ttl})
        
            table.update_item(
                Key={"ip": counter_key},
                UpdateExpression="SET #c = if_not_exists(#c, :zero) + :one",
                ExpressionAttributeNames={"#c": "count"},
                ExpressionAttributeValues={":zero": 0, ":one": 1}
            )
        
        result = table.get_item(Key={"ip": counter_key})
        count = result.get("Item", {}).get("count", 0)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({ "count": int(count) })
        }

    except Exception as e:
        print("Error:", str(e))  # already present
        import traceback
        traceback.print_exc()    # Add this line to get full traceback in CloudWatch logs
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({ "error": "Internal server error" })
        }

