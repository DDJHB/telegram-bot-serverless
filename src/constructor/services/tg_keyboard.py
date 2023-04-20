import json


def build_view_keyboard(items: list[dict]) -> dict:
    inline_keyboard = [build_navigation_buttons()]
    for item in items:
        inline_keyboard.append(build_single_route_button(item))

    return {
        "inline_keyboard": inline_keyboard
    }


def extend_keyboard_with_modify_buttons(keyboard_definition, n_rows) -> dict:
    keyboard_list = keyboard_definition["inline_keyboard"]
    for index in range(n_rows):
        keyboard_list.append(build_single_indexed_button(index))

    return {
        "inline_keyboard": keyboard_list
    }


def build_single_indexed_button(index: int) -> list[dict]:
    return [{"text": str(index), "callback_data": str(index)}]


def build_single_route_button(route_info: dict) -> list[dict]:
    return [{"text": route_info.get("routeName", "random"), "url": construct_google_maps_url(route_info)}]


def build_navigation_buttons() -> list[dict]:
    return [
        {
            "text": "back",
            "callback_data": "back",
        },
        {
            "text": "next",
            "callback_data": "next",
        },
    ]


def construct_google_maps_url(route_info: dict):
    destination = json.loads(route_info["destinationLocation"])
    source = json.loads(route_info["sourceLocation"])

    base_url = "https://www.google.com/maps/dir/?api=1"
    origin = f"&origin={source['latitude']},{source['longitude']}"
    destination = f"&destination={destination['latitude']},{destination['longitude']}"
    travel_mode = "&travelmode=driving"
    url = base_url + origin + destination + travel_mode
    return url

