import json
import time
from datetime import datetime
from uuid import uuid4
import geohash

import boto3
from boto3.dynamodb.conditions import Key, Attr

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


def put_passenger_route(driver_route: dict, username: str, chat_id: int):
    passenger_route = driver_route | {
        "sk": make_key(PASSENGER_TYPENAME, username),
        "gsi3pk": make_key(PASSENGER_TYPENAME, username),
        "gsi3sk": make_key(PASSENGER_TYPENAME, username),
        "chat_id": chat_id,
        "username": username,
    }

    proximity_indexes_attributes = [
        "source_geohash_close",
        "destination_geohash_close",
        "source_geohash_mid",
        "destination_geohash_mid",
        "source_geohash_long",
        "destination_geohash_long",
    ]

    obfuscate_driver_attributes = [
        "joined_users_count"
    ]

    for attribute in proximity_indexes_attributes:
        passenger_route.pop(attribute)

    for attribute in obfuscate_driver_attributes:
        passenger_route.pop(attribute)

    table.put_item(Item=passenger_route)


def put_route(username: str, chat_id: int, route_name: str, route_info: dict):
    route_id = str(uuid4())
    source_location = route_info['sourceLocation']
    destination_location = route_info['destinationLocation']

    route_info_fixed = prepare_inner_dicts_for_db(route_info)
    start_time_epoch = int(datetime.strptime(f"{route_info['rideStartTime']} +0400", "%d.%m.%Y %H:%M %z").timestamp())
    table.put_item(
        Item={
            **route_info_fixed,
            "pk": make_key(ROUTE_TYPENAME, route_id),
            "sk": make_key(DRIVER_TYPENAME, username),
            "gsi3pk": make_key(DRIVER_TYPENAME, username),
            "gsi3sk": make_key(DRIVER_TYPENAME, username),
            "gsi4pk": "START_TIME",
            "approval_info": json.dumps({
                "start": {
                    "YES": 0,
                    "NO": 0,
                },
                "end": {
                    "YES": 0,
                    "NO": 0,
                },
            }),
            "has_started": False,
            "has_ended": False,
            "joined_users_count": 0,
            "route_name": route_name,
            "route_id": route_id,
            "owner_username": username,
            "owner_chat_id": chat_id,
            "username": username,
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
    is_passenger: bool = False,
):
    typename = DRIVER_TYPENAME if not is_passenger else PASSENGER_TYPENAME
    query_args = {
        "KeyConditionExpression": (
                Key('gsi3pk').eq(make_key(typename, username))
                &
                Key('gsi3sk').eq(make_key(typename, username))
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


def get_routes_by_proximity(
    proximity: str,
    source_geohash: str,
    destination_geohash: str,
    limit: int = 5,
    filter_by_time: bool = False,
    range: tuple = (),
    last_key: dict = None
):
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

    if last_key:
        query_args.update({"ExclusiveStartKey": last_key})

    if filter_by_time:
        lb_epoch, ub_epoch = range
        query_args.update({"FilterExpression": Attr("start_time_epoch").between(lb_epoch, ub_epoch)})

    response = table.query(
        IndexName=index_name,
        Limit=limit,
        **query_args
    )
    return response


def get_routes_by_start_time(time_left: int):
    now = int(time.time())

    query_args = {
        "KeyConditionExpression": (
                Key("gsi4pk").eq("START_TIME")
                &
                Key("start_time_epoch").between(now + time_left * 3600 - 150, now + time_left * 3600 + 150)
        ),
    }


    response = table.query(
        IndexName="gsi4",
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


def delete_passenger_route(username: str, route_id: str):
    table.delete_item(
        Key={
            "pk": make_key(ROUTE_TYPENAME, route_id),
            "sk": make_key(PASSENGER_TYPENAME, username),
        }
    )


def passenger_route_exists(username: str, route_id: str):
    response = table.get_item(
        Key={
            "pk": make_key(ROUTE_TYPENAME, route_id),
            "sk": make_key(PASSENGER_TYPENAME, username)
        }
    )

    return response.get("Item")


def collect_associated_route_records(route_id):
    driver_route = get_route_by_id(route_id)
    passenger_routes = get_passengers_routes_by_route_id(route_id).get("Items", [])
    print([driver_route] + passenger_routes)
    return [driver_route] + passenger_routes


def delete_routes(routes):
    for route in routes:
        table.delete_item(
            Key={
                "pk": route["pk"],
                "sk": route["sk"],
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
