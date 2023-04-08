import json

from src.database.chat_state import update_chat_state, get_chat_state
from src.database.routes import get_user_routes
from src.constructor.bot_response import respond_with_inline_keyboard

keyboard_name = "routes_keyboard"


def handler(data):
    chat_id = data["message"]["chat"]["id"]
    username = data['message']['from']['username']
    chat_state = get_chat_state(chat_id)

    response = get_user_routes(username)
    keyboard_definition = build_keyboard(response['Items'])
    tg_response = respond_with_inline_keyboard(
        parent_message="Your routes:",
        keyboard_definition=keyboard_definition,
        chat_id=chat_id,
    )
    keyboard_id = str(tg_response.json()['result']["message_id"])
    current_page = 1
    global_keyboards_info = json.loads(chat_state.get("global_keyboards_info") or '{}')
    global_keyboards_info.update(
        {
            keyboard_id: {
                "keyboard_name": "routes_keyboard",
                "page_info": {
                    "last_evaluated_keys": {str(current_page): response['LastEvaluatedKey']},
                    "current_page_number": current_page,
                },
            }
        }
    )

    chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})

    command_state = {
        "active_command": 'showMyRoutes',
        "current_step_index": 0,
        "command_info": json.dumps({}),
    }
    chat_state.update(command_state)

    update_chat_state(chat_state)

    return "Wait"


def build_keyboard(items: list[dict]) -> dict:
    inline_keyboard = [build_navigation_buttons()]
    for item in items:
        inline_keyboard.append(build_single_route_button(item))

    return {
        "inline_keyboard": inline_keyboard
    }


def build_single_route_button(route_info: dict) -> list[dict]:
    return [{"text": route_info.get("route_id", "random"), "callback_data": "wow"}]


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
