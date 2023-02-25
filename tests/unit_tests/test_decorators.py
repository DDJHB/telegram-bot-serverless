import json


def test_standard_api_handler():
    from src.constructor.decorators import standard_api_handler

    test_event = {
        'body': json.dumps({
            "test_key": "test_value"
        })
    }

    @standard_api_handler
    def greet_with_test_key(event, _context):
        return {
            "statusCode": 200,
            "body": f"Hello World\n{event['body'].get('test_key')}"
        }

    response = greet_with_test_key(test_event, {})
    assert response['statusCode'] == 200
    assert isinstance(response['body'], str)


