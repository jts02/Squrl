"""Squrl lambda function."""
import datetime
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
        self.registry = {"GET": self.get, "POST": self.post}

    def get(self, url, **kwargs):
        """Return a key if one exists."""
        key = self.get_key(url)

        return key if self.key_exists(key) else ""

    def post(self, url, **kwargs):
        """Create or update key."""
        return self.create_key(url, **kwargs)

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

    @staticmethod
    def get_key(url):
        """Get a short key for the url prefixed with 'u/' plus 7 characters."""
        digest = hashlib.md5(url.encode()).hexdigest()
        return f"u/{digest[:7]}"

    def create_key(self, url, days=7):
        """Create the short key object with an expiration and redirect."""
        expires = datetime.datetime.now() + datetime.timedelta(days=days)
        key = self.get_key(url)

        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            WebsiteRedirectLocation=url,
            Expires=expires,
            ContentType="text/plain"
        )

        return key

    @staticmethod
    def get_response(response="OK", error=None):
        """Get a proper, formatted response."""
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
    """
    Handle the lambda function event and return a response with
    a body containing the url and the key, if it exists.

    response body: '{"url": <string>, "key": <string>}'
    """
    squrl = Squrl(boto3.client("s3"), os.getenv("S3_BUCKET"))
    url = event["queryStringParameters"]["url"]
    method = event["httpMethod"]

    if method in squrl.registry.keys():
        key = squrl.registry[method](url)

        return squrl.get_response(response={"url": url, "key": key})
    else:
        error = ValueError(f"Unsupported method: {method}")

        return squrl.get_response(error=error)
