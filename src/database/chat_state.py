import boto3
import json


resource = boto3.resource('dynamodb')
table = resource.Table('user-chat-state-table')


def put_chat_state_record(chat_id: int, state: dict, extra_fields: dict):
    table.put_item(
        Item={
            "pk": chat_id,
            "chat_id": chat_id,
            "state": json.dumps(state),
            **extra_fields,
        }
    )


def get_chat_state_record(chat_id: int):
    response = table.get_item(
        Key={
            'pk': chat_id
        }
    )

    return response.get('Item') or None
