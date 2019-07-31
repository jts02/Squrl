import json

import boto3
from botocore.stub import Stubber, ANY
from pytest import fixture, raises

from squrl import Squrl


def test_get_key_success():
    client = boto3.client("s3")
    stub = Stubber(client)
    bucket = "test-bucket"
    url = "https://fake.example.com"

    stub.add_client_error(
        "head_object",
        expected_params={"Bucket": bucket, "Key": ANY},
        service_error_code="404"
    )
    stub.add_response(
        "put_object",
        {"VersionId": "1"},
        expected_params={
            "Bucket": bucket, "Key": ANY, "WebsiteRedirectLocation": url
        }
    )
    stub.activate()

    squrl = Squrl(client, bucket)
    key = squrl.get_key(url)

    assert key and key.startswith("u/")
    stub.assert_no_pending_responses()


def test_get_key_failure():
    client = boto3.client("s3")
    stub = Stubber(client)
    bucket = "test-bucket"
    url = "https://fake.example.com"

    for _ in range(3):
        stub.add_response(
            "head_object",
            expected_params={"Bucket": bucket, "Key": ANY},
            service_response={}
        )
    stub.activate()

    with raises(ValueError):
        Squrl(client, bucket).get_key(url, length=30)


@fixture(scope="function")
def response():
    return {
        "origin_url": "origin_url",
        "short_url": "short_url"
    }


def test_response_successful(response):
    actual_response = Squrl.get_response(response=response)
    expected_response = {
        "statusCode": "200",
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }

    assert actual_response == expected_response


@fixture(scope="function")
def error():
    return ValueError("The error")


def test_response_failed():
    actual_response = Squrl.get_response(error=error)
    expected_response = {
        "statusCode": "400",
        "body": str(error),
        "headers": {
            "Content-Type": "application/json"
        }
    }

    assert actual_response == expected_response
