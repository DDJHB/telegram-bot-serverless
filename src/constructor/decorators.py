import json

import requests


def standard_api_handler(fn):
    def decorator(event, _context):
        # for testing purposes
        url = "https://eow4z7ghug68ys0.m.pipedream.net"
        requests.post(
            url=url,
            json={
                "event": event
            }
        )
        # normalize event body
        event['body'] = json.loads(event['body'])

        # handle the request
        response = fn(event, _context)

        # normalize response body
        if 'body' in response:
            response['body'] = json.dumps(response['body'])

        return response

    return decorator
