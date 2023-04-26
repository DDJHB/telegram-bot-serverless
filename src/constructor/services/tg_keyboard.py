import json

from src.database.routes import get_user_routes
from src.database.chat_state import update_chat_state
from src.constructor.bot_response import update_inline_keyboard


def build_approval_keyboard(item):
    inline_keyboard = [[{"text": "YES", "callback_data": "YES+".join(item.get("route_id"))}],
                       [{"text": "NO", "callback_data": "NO+".join(item.get("route_id"))}]]

    return {
        "inline_keyboard": inline_keyboard
    }


def build_view_keyboard(items: list[dict]) -> dict:
    inline_keyboard = [build_navigation_buttons()]
    for item in items:
        inline_keyboard.append(build_single_route_button(item))

    return {
        "inline_keyboard": inline_keyboard
    }


def extend_keyboard_with_route_id_buttons(keyboard_definition, routes) -> dict:
    keyboard_list = keyboard_definition["inline_keyboard"]
    index_buttons_rows = []
    for index, route in enumerate(routes):
        route_id = route["route_id"]
        index_buttons_rows.append(build_single_indexed_route_button(route_id, index))

    keyboard_list.append(index_buttons_rows)
    return {
        "inline_keyboard": keyboard_list
    }


def build_indexed_keyboard(items: list) -> dict:
    inline_keyboard = []
    for index, item in enumerate(items):
        inline_keyboard.append(build_indexed_button(item, index))

    return {
        "inline_keyboard": inline_keyboard
    }


def build_rating_keyboard(route_id: str) -> dict:
    inline_keyboard = []
    for i in range(1, 6):
        inline_keyboard.append(build_single_indexed_route_button(route_id, i))

    return {
        "inline_keyboard": inline_keyboard
    }


def build_single_indexed_route_button(route_id: str, index: int) -> dict:
    return {"text": str(index + 1), "callback_data": route_id}


def build_single_route_button(route_info: dict) -> list[dict]:
    return [{"text": route_info.get("routeName", "random"), "url": construct_google_maps_url(route_info)}]


def build_indexed_button(item: str, index: int) -> list[dict]:
    return [{"text": item, "callback_data": index}]


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

def handle_navigation_buttons(keyboard_id, callback_query, chat_state):
    button_name = callback_query["data"]
    username = callback_query["from"]["username"]
    chat_id = callback_query["message"]["chat"]["id"]

    global_keyboards_info = json.loads(chat_state.get("global_keyboards_info") or '{}')
    keyboard_info = global_keyboards_info[keyboard_id]

    if button_name == "next":
        page_info = keyboard_info["page_info"]
        current_page_number = page_info["current_page_number"]
        last_evaluated_key = page_info["last_evaluated_keys"][str(current_page_number)]

        response = get_user_routes(username, limit=5, last_key=last_evaluated_key)
        items = response['Items']

        # TODO MOVE DOWN U STUPID MORON
        keyboard_definition = build_view_keyboard(items)
        update_inline_keyboard(chat_id, keyboard_id, keyboard_definition)

        new_last_evaluated_key = response.get('LastEvaluatedKey')
        new_page_number = current_page_number + 1

        page_info["last_evaluated_keys"][str(new_page_number)] = new_last_evaluated_key
        page_info["current_page_number"] = new_page_number
        global_keyboards_info[keyboard_id].update({"page_info": page_info})

        chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})
        update_chat_state(chat_state)

    elif button_name == "back":
        page_info = keyboard_info["page_info"]
        current_page_number = page_info["current_page_number"]
        if current_page_number == 1:
            return ""

        needed_page_number = current_page_number - 2

        needed_page_le_key = page_info["last_evaluated_keys"].get(str(needed_page_number))
        response = get_user_routes(username, limit=5, last_key=needed_page_le_key)
        items = response['Items']

        keyboard_definition = build_view_keyboard(items)
        update_inline_keyboard(chat_id, keyboard_id, keyboard_definition)

        new_last_evaluated_key = response.get('LastEvaluatedKey')
        new_page_number = current_page_number - 1

        page_info["last_evaluated_keys"][str(new_page_number)] = new_last_evaluated_key
        page_info["current_page_number"] = new_page_number
        global_keyboards_info[keyboard_id].update({"page_info": page_info})

        chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})
        update_chat_state(chat_state)
