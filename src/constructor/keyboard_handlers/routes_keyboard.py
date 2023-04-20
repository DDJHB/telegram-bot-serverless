import json

from src.constructor.services.tg_keyboard import build_navigation_buttons, build_single_route_button
from src.database.routes import get_user_routes
from src.database.chat_state import update_chat_state
from src.constructor.bot_response import update_inline_keyboard


def handler(keyboard_id, callback_query, chat_state):
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
        nav_buttons_definition = build_navigation_buttons()
        keyboard_definition = build_keyboard(items, nav_buttons_definition)
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

        nav_buttons_definition = build_navigation_buttons()
        keyboard_definition = build_keyboard(items, nav_buttons_definition)
        update_inline_keyboard(chat_id, keyboard_id, keyboard_definition)

        new_last_evaluated_key = response.get('LastEvaluatedKey')
        new_page_number = current_page_number - 1

        page_info["last_evaluated_keys"][str(new_page_number)] = new_last_evaluated_key
        page_info["current_page_number"] = new_page_number
        global_keyboards_info[keyboard_id].update({"page_info": page_info})

        chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})
        update_chat_state(chat_state)


def build_keyboard(items, nav_buttons_definition):
    inline_keyboard = [nav_buttons_definition]
    for item in items:
        inline_keyboard.append(build_single_route_button(item))

    return {
        "inline_keyboard": inline_keyboard
    }
