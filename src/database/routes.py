import json
from datetime import datetime
from uuid import uuid4
import geohash

import boto3
from boto3.dynamodb.conditions import Key

resource = boto3.resource('dynamodb')
table = resource.Table('routes-table-v2')

DRIVER_TYPENAME = "DRIVER"
PASSENGER_TYPENAME = "PASSENGER"
ROUTE_TYPENAME = "ROUTE"

index_name_by_precision = {
    6: "close_range_routes_geohash",
    5: "mid_range_routes_geohash",
    4: "long_range_routes_geohash",
}


def map_proximity_to_precision(proximity: str) -> int:
    precision_by_proximity = {
        "long": 4,
        "mid": 5,
        "close": 6,
    }

    precision = precision_by_proximity.get(proximity)
    print("Geo Precision: ", precision)

    return precision


def get_route_by_id_and_username(route_id: str, username: str):
    response = table.get_item(
        Key={
            'pk': make_key(ROUTE_TYPENAME, route_id),
            'sk': make_key(DRIVER_TYPENAME, username),
        }
    )

    return response.get('Item')


def get_route_by_id(route_id: str):
    query_args = {
        "KeyConditionExpression": (
                Key('pk').eq(make_key(ROUTE_TYPENAME, route_id))
                &
                Key('sk').begins_with(DRIVER_TYPENAME)
        ),
    }

    response = table.query(**query_args)
    items = response['Items']
    if len(items) < 1:
        return None

    return items[0]


def get_passengers_routes_by_route_id(route_id: str):
    query_args = {
        "KeyConditionExpression": (
                Key('pk').eq(make_key(ROUTE_TYPENAME, route_id))
                &
                Key('sk').begins_with(PASSENGER_TYPENAME)
        ),
    }

    response = table.query(**query_args)
    return response


def put_route(username: str, chat_id: int, route_name: str, route_info: dict):
    route_id = str(uuid4())
    source_location = route_info['sourceLocation']
    destination_location = route_info['destinationLocation']

    route_info_fixed = prepare_inner_dicts_for_db(route_info)
    start_time_epoch = int(datetime.strptime(route_info["rideStartTime"], "%d.%m.%Y %H:%M").timestamp())
    table.put_item(
        Item={
            **route_info_fixed,
            "pk": make_key(ROUTE_TYPENAME, route_id),
            "sk": make_key(DRIVER_TYPENAME, username),
            "gsi3pk": make_key(DRIVER_TYPENAME, username),
            "gsi3sk": make_key(DRIVER_TYPENAME, username),
            "approval_info": json.dumps(
                {
                    "YES": 0,
                    "NO": 0,
                }
            ),
            "joined_users_count": 0,
            "route_name": route_name,
            "route_id": route_id,
            "owner_username": username,
            "owner_chat_id": chat_id,
            "chat_id": chat_id,
            "start_time_epoch": start_time_epoch,
            "source_geohash_close": geohash.encode(**source_location, precision=6),
            "destination_geohash_close": geohash.encode(**destination_location, precision=6),
            "source_geohash_mid": geohash.encode(**source_location, precision=5),
            "destination_geohash_mid": geohash.encode(**destination_location, precision=5),
            "source_geohash_long": geohash.encode(**source_location, precision=4),
            "destination_geohash_long": geohash.encode(**destination_location, precision=4),
        }
    )


def update_route(route_record):
    table.put_item(Item=route_record)


def get_user_routes(
        username: str,
        limit: int = 5,
        last_key: 'dict|None' = None,
):
    query_args = {
        "KeyConditionExpression": (
                Key('gsi3pk').eq(make_key(DRIVER_TYPENAME, username))
                &
                Key('gsi3sk').eq(make_key(DRIVER_TYPENAME, username))
        ),
        "Limit": limit,
    }
    if last_key:
        query_args.update({"ExclusiveStartKey": last_key})

    response = table.query(**query_args, IndexName="gsi3")
    return response


def get_route_by_name(username: str, route_name: str):
    query_args = {
        "KeyConditionExpression": (
                Key('owner_username').eq(username)
                &
                Key('route_name').eq(route_name)
        ),
    }
    response = table.query(
        IndexName="gsi2",
        **query_args
    )
    items = response.get('Items', [])
    if len(items) < 1:
        return None

    return items[0]


def get_routes_by_proximity(proximity: str, source_geohash: str, destination_geohash: str):
    precision = map_proximity_to_precision(proximity)
    index_name = index_name_by_precision.get(precision)

    gsi_pk = f"source_geohash_{proximity}"
    gsi_sk = f"destination_geohash_{proximity}"

    query_args = {
        "KeyConditionExpression": (
                Key(gsi_pk).eq(source_geohash)
                &
                Key(gsi_sk).eq(destination_geohash)
        ),
    }
    response = table.query(
        IndexName=index_name,
        **query_args
    )
    return response


def delete_user_route(pk, sk):
    table.delete_item(
        Key={
            "pk": pk,
            "sk": sk,
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


def make_key(*args):
    return "#".join(args)
