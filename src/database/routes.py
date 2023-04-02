import json
from datetime import datetime
from uuid import uuid4

import boto3


resource = boto3.resource('dynamodb')
table = resource.Table('routes-table')


def put_route(username: str, chat_id: int, route_info: dict):
    route_id = str(uuid4())
    route_info_fixed = prepare_inner_dicts_for_db(route_info)
    start_time_epoch = int(datetime.strptime(route_info["rideStartTime"],"%d.%m.%Y %H:%M").timestamp())
    table.put_item(
        Item={
            **route_info_fixed,
            "route_id": route_id,
            "owner_username": username,
            "chat_id": chat_id,
            "start_time_epoch": start_time_epoch,
        }
    )


def prepare_inner_dicts_for_db(info):
    new_info = {}
    for key in info.keys():
        if isinstance(info[key], dict):
            new_info[key] = json.dumps(info[key])
        else:
            new_info[key] = info[key]
    return new_info
