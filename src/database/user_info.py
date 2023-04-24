import boto3
from decimal import Decimal


resource = boto3.resource('dynamodb')
table = resource.Table('user-info-table')


def reparse_floats_for_dynamo(item: dict):
    formatted_item = {}
    for key in item.keys():
        formatted_item[key] = item[key]
        if isinstance(item[key], float):
            formatted_item[key] = Decimal(item[key])

    return formatted_item


def put_user_info_record(username: str, wallet_address: str, private_key: str, rating: float, raters_num: int, extra_fields: dict):
    item = {
        "pk": username,
        "wallet_address": wallet_address,
        "private_key": private_key,
        "rating": rating,
        "raters_num": raters_num,
        **extra_fields,
    }
    table.put_item(
        Item=reparse_floats_for_dynamo(item)
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



