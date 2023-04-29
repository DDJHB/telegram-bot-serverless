import boto3

from boto3.dynamodb.conditions import Key

resource = boto3.resource('dynamodb')
table = resource.Table('user-chat-state-table')


def put_chat_state(chat_id: int, other_fields: dict):
    chat_state = {
        "pk": chat_id,
        "chat_id": chat_id,
        **other_fields,
    }
    table.put_item(Item=chat_state)
    return chat_state


def update_chat_state(new_record: dict):
    table.put_item(Item=new_record)


def get_chat_state(chat_id: int):
    response = table.get_item(
        Key={
            'pk': chat_id
        }
    )

    return response.get('Item')


def get_chat_state_by_username(username: str):
    query_args = {
        "KeyConditionExpression": (
            Key('username').eq(username)
        ),
    }

    response = table.query(
        IndexName="gsi1",
        **query_args
    )
    items = response.get('Items', [])
    if len(items) < 1:
        return None

    return items[0]
