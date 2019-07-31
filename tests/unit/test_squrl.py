import json

import boto3
from botocore.stub import Stubber, ANY
from pytest import fixture

from squrl import Squrl


@fixture(scope="function")
def stubber(request):
    client = boto3.client("s3")
    stub = Stubber(client)

    request.addfinalizer(stub.assert_no_pending_responses)

    return {
        "client": client,
        "stub": stub
    }


def test_key_exists(stubber):
    expected_params = {
        "Bucket": ANY,
        "Key": ANY
    }

    stubber["stub"].add_response(
        "head_object", {}, expected_params=expected_params
    )
    stubber["stub"].activate()

    assert Squrl(stubber["client"], "test-bucket").key_exists("test-key")


def test_key_does_not_exist(stubber):
    expected_params = {
        "Bucket": ANY,
        "Key": ANY
    }

    stubber["stub"].add_client_error(
        "head_object",
        expected_params=expected_params,
        service_error_code="404"
    )
    stubber["stub"].activate()

    assert not Squrl(stubber["client"], "test-bucket").key_exists("test-key")


def test_get_key():
    key = Squrl.get_key("test-url")

    assert len(key) == 9
    assert key.startswith("u/")


def test_create_key(stubber):
    url = "test-url"
    content_type = "text/plain"
    expected_params = {
        "Bucket": ANY,
        "Key": ANY,
        "WebsiteRedirectLocation": url,
        "Expires": ANY,
        "ContentType": content_type
    }

    stubber["stub"].add_response(
        "put_object", {}, expected_params=expected_params
    )
    stubber["stub"].activate()

    Squrl(stubber["client"], "test-bucket").create_key("test-url")


def test_get_response_ok():
    response = "test-body"
    expected_response = {
        "statusCode": "200",
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json",
        },
    }
    actual_response = Squrl.get_response(response=response)

    assert expected_response == actual_response


def test_get_response_error():
    error = ValueError("test-error")
    expected_response = {
        "statusCode": "400",
        "body": str(error),
        "headers": {
            "Content-Type": "application/json",
        },
    }
    actual_response = Squrl.get_response(error=error)

    assert expected_response == actual_response
