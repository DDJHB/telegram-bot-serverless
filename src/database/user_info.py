import boto3
import json


resource = boto3.resource('dynamodb')
table = resource.Table('user-info-table')


def put_wallet_info_record(username: str, wallet_address: str, private_key: str, extra_fields: dict):
    table.put_item(
        Item={
            "pk": username,
            "wallet_address": wallet_address,
            "private_key": private_key,
            **extra_fields,
        }
    )


def get_wallet_info_record(username: str):
    response = table.get_item(
        Key={
            'pk': username
        }
    )

    return response.get('Item') or None


def delete_wallet_info_record(username: str):
    table.delete_item(
        Key={
            'pk': username
        }
    )


def update_wallet_info_record(username: str, wallet_address: str, private_key: str, extra_fields: dict):
    delete_wallet_info_record(username)
    put_wallet_info_record(username, wallet_address, private_key, extra_fields)



