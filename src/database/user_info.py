import boto3
import json


resource = boto3.resource('dynamodb')
table = resource.Table('user-info-table')


def put_user_info_record(username: str, wallet_address: str, private_key: str, rating: float, raters_num: int, extra_fields: dict):
    table.put_item(
        Item={
            "pk": username,
            "wallet_address": wallet_address,
            "private_key": private_key,
            "rating": rating,
            "raters_num": raters_num,
            **extra_fields,
        }
    )


def get_user_info_record(username: str):
    response = table.get_item(
        Key={
            'pk': username
        }
    )

    return response.get('Item') or None


def delete_user_info_record(username: str):
    table.delete_item(
        Key={
            'pk': username
        }
    )


def update_user_info(new_record: dict):
    table.put_item(Item=new_record)



