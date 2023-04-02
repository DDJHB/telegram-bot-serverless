import boto3
from datetime import datetime


resource = boto3.resource('dynamodb')
table = resource.Table('ethereum-transactions-table')


def put_transaction_request(tx_hash: str, chat_id: int, extra_fields: dict[str, str]) -> None:
    table.put_item(
        Item={
            "pk": tx_hash,
            "gsi1_pk": chat_id,
            "chat_id": chat_id,
            "timestamp": str(datetime.utcnow()),
            **extra_fields,
        }
    )


def get_transaction(tx_hash: str) -> dict[str, str]:
    response = table.get_item(
        Key={
            'pk': tx_hash
        }
    )

    return response['Item']
