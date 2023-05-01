import json

import requests


def standard_api_handler(fn):
    def decorator(event, _context):
        # normalize event body
        event['body'] = json.loads(event['body'])

        # handle the request
        response = fn(event, _context)

        # normalize response body
        if 'body' in response:
            response['body'] = json.dumps(response['body'])

        return response

    return decorator
