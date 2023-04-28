import json

from src.constructor.bot_response import respond_with_text, respond_with_inline_keyboard
from src.constructor.services.tg_keyboard import build_rating_keyboard
from src.database.chat_state import update_chat_state, get_chat_state


def rate_driver(route: dict):
    route_id = route["route_id"]
    chat_id = route['chat_id']
    chat_state = get_chat_state(chat_id)

    keyboard_def = build_rating_keyboard(route_id)
    tg_response = respond_with_inline_keyboard(
        parent_message="Please, rate the driver: ",
        keyboard_definition=keyboard_def,
        chat_id=chat_id,
    )

    keyboard_id = str(tg_response.json()['result']["message_id"])
    global_keyboards_info = json.loads(chat_state.get("global_keyboards_info") or '{}')
    global_keyboards_info.update(
        {
            keyboard_id: {
                "keyboard_name": "rate_driver_keyboard",
            }
        }
    )

    chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})
    update_chat_state(chat_state)

