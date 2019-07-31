"""Squrl lambda function."""
import hashlib
import json
import os

import boto3
import botocore.exceptions


class Squrl:
    """Squrl makes URL's shorter."""

    def __init__(self, client, bucket):
        """Override init."""
        self.client = client
        self.bucket = bucket

    def key_exists(self, key):
        """Return True if the specified key exists."""
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                raise e

        return True

    def get_key(self, url, length=7):
        """
        Get the shortened path for the url prefixed with 'u/'.

        Raise ValueError - Invalid key length if the length is less than 1
        or greater than the length of the hexdigest.
        Raise ValueError - Key exists if all possible keys with this
        hexdigest already exist.
        """
        digest = hashlib.md5(url.encode()).hexdigest()
        key = None

        if length < 1 or length > len(digest):
            raise ValueError(f"Invalid key length: {length}")

        for i in range(len(digest) - length + 1):
            key = f"u/{digest[i:i+length]}"

            if not self.key_exists(key):
                self.client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    WebsiteRedirectLocation=url
                )
                return key

        raise ValueError(f"Key exists: {key}")

    @staticmethod
    def get_response(response="OK", error=None):
        """Get a poper, formatted response."""
        statusCode = "400" if error else "200"
        body = str(error) if error else json.dumps(response)

        return {
            "statusCode": statusCode,
            "body": body,
            "headers": {
                "Content-Type": "application/json",
            },
        }


def handler(event, context):
    """Handle the lambda function event and return a response."""
    squrl = Squrl(boto3.client("s3"), os.getenv("S3_BUCKET"))
    url = event["queryStringParameters"]["url"]
    key = squrl.get_key(url, length=7)

    return squrl.respond({"url": url, "key": key})
