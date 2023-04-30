import geohash
import pytz

from datetime import datetime

from src.database.routes import map_proximity_to_precision, get_routes_by_proximity


def compute_routes(user_route_info: dict, last_key: dict = None):
    user_start_location = user_route_info["sourceLocation"]
    user_end_location = user_route_info["destinationLocation"]
    proximity = user_route_info["searchProximity"]
    time_range = user_route_info["rideStartTimeRange"]
    lb_time, ub_time = map(lambda x: x.strip(), time_range.split("-"))
    lb_epoch, ub_epoch = compute_epoch(lb_time), compute_epoch(ub_time)

    precision = map_proximity_to_precision(proximity)

    user_start_geohash = geohash.encode(**user_start_location, precision=precision)
    user_end_geohash = geohash.encode(**user_end_location, precision=precision)

    routes = []
    while len(routes) < 5:
        routes_info = get_routes_by_proximity(
            proximity,
            user_start_geohash,
            user_end_geohash,
            filter_by_time=True,
            range=(lb_epoch, ub_epoch),
            last_key=last_key,
        )
        print(routes_info)
        routes.extend(routes_info.get("Items", []))
        if not (last_key := routes_info.get("LastEvaluatedKey")):
            break

    routes_info = {
        "Items": routes,
        "LastEvaluatedKey": build_last_key(routes[-1], proximity) if routes else None,
    }

    return routes_info


def compute_epoch(time_a):
    date_format = "%d.%m.%Y %H:%M"
    timezone = pytz.timezone('Etc/GMT-4')
    return int(timezone.localize(datetime.strptime(time_a, date_format)).timestamp())


def build_last_key(route, range):
    return {
        "pk": route["pk"],
        "sk": route["sk"],
        f"destination_geohash_{range}": route[f"destination_geohash_{range}"],
        f"source_geohash_{range}": route[f"source_geohash_{range}"],
    }