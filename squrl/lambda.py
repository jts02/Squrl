"""
Squrl lambda handler
"""
import hashlib
import json


def squrlify(url, path="squrl", size=7):
    """
    Get the shortened path for the url.
    """
    digest = hashlib.md5(url.encode()).hexdigest()
    # TODO check for collision
    return f"{path}/{digest[:size]}"


def respond(err, res=None):
    statusCode = "400" if err else "200"
    body = err.message if err else json.dumps(res)

    return {
        "statusCode": statusCode,
        "body": body,
        "headers": {
            "Content-Type": "application/json",
        },
    }


def handler(event, context):
    origin_url = event["queryStringParameters"]["url"]
    short_url = hashlib.md5(origin_url.encode()).hexdigest()[:7]

    response = {
        "origin_url": origin_url,
        "short_url": short_url
    }

    return respond(response)
