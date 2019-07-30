import json

from pytest import fixture

import squrl


@fixture(scope="function")
def response():
    return {
        "origin_url": "origin_url",
        "short_url": "short_url"
    }


def test_response_successful(response):
    actual_response = squrl.respond(response)
    expected_response = {
        "statusCode": "200",
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json",
        },
    }

    assert actual_response == expected_response
