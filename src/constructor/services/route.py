import geohash

from src.database.routes import map_proximity_to_precision, get_routes_by_proximity


def compute_routes(user_route_info: dict, last_key: dict = None):
    user_start_location = user_route_info["sourceLocation"]
    user_end_location = user_route_info["destinationLocation"]
    proximity = user_route_info["searchProximity"]

    precision = map_proximity_to_precision(proximity)

    user_start_geohash = geohash.encode(**user_start_location, precision=precision)
    user_end_geohash = geohash.encode(**user_end_location, precision=precision)

    routes_info = get_routes_by_proximity(proximity, user_start_geohash, user_end_geohash, last_key=last_key)
    print(routes_info)
    return routes_info
