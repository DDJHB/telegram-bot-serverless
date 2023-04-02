import boto3


resource = boto3.resource('dynamodb')
table = resource.Table('user-chat-state-table')


def put_chat_state(chat_id: int, other_fields: dict):
    table.put_item(
        Item={
            "pk": chat_id,
            "chat_id": chat_id,
            **other_fields,
        }
    )


def update_chat_state(new_record: dict):
    table.put_item(Item=new_record)


def get_chat_state(chat_id: int):
    response = table.get_item(
        Key={
            'pk': chat_id
        }
    )

    return response.get('Item')
