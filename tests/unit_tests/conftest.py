import moto
import boto3
import pytest


@pytest.fixture(scope="session", autouse=True)
def chat_state_table():
    print(2)
    with moto.mock_dynamodb:
        client = boto3.client("dynamodb")
        client.create_table(
            **{
                "TableName": "user-chat-state-table",
                "AttributeDefinitions": [
                    {
                        "AttributeName": "pk",
                        "AttributeType": "N"
                    }
                ],
                "KeySchema": [
                    {
                        "AttributeName": "pk",
                        "KeyType": "HASH"
                    }
                ],
                "BillingMode": "PAY_PER_REQUEST"
            }
        )
        yield
