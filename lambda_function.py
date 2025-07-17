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
    pk_ip = f"IP#{hashed_ip}"
    pk_counter = "COUNTER#global"

    try:
        # Check if IP has already visited recently
        response = table.get_item(Key={"pk": pk_ip})
        if "Item" not in response:
            # New visitor — log hashed IP with TTL
            ttl = int(time.time()) + TTL_DURATION
            table.put_item(Item={"pk": pk_ip, "ttl": ttl})

            # Increment the global counter
            table.update_item(
                Key={"pk": pk_counter},
                UpdateExpression="SET #c = if_not_exists(#c, :zero) + :one",
                ExpressionAttributeNames={"#c": "count"},
                ExpressionAttributeValues={":zero": 0, ":one": 1}
            )

        # Get the updated count
        result = table.get_item(Key={"pk": pk_counter})
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

