import json

from src.constructor.bot_response import respond_with_inline_keyboard
from src.constructor.services.tg_keyboard import build_notification_view_keyboard
from src.database.chat_state import get_chat_state, update_chat_state
from src.database.routes import get_routes_by_start_time


keyboard_name = "route_notification_keyboard"
def handler(event, context):
    try:
        routes_1_hour = get_routes_by_start_time(1)
        routes_24_hour = get_routes_by_start_time(24)
        print(routes_1_hour, routes_24_hour)

        for item in routes_1_hour.get('Items', []):
            keyboard_def = build_notification_view_keyboard(item)
            tg_response = respond_with_inline_keyboard(
                parent_message=f"One hour left till {item['route_name']} route!",
                keyboard_definition=keyboard_def,
                chat_id=item['chat_id']
            )
            handle_keyboard(tg_response, item)

        for item in routes_24_hour.get('Items', []):
            keyboard_def = build_notification_view_keyboard(item)
            tg_response = respond_with_inline_keyboard(
                parent_message=f"One day left till {item['route_name']} route!",
                keyboard_definition=keyboard_def,
                chat_id=item['chat_id']
            )
            handle_keyboard(tg_response, item)

        return {'statusCode': 200}
    except Exception as error:
        print(error)
        return {'statusCode': 200}


def handle_keyboard(tg_response, item: dict):
    keyboard_id = str(tg_response.json()['result']["message_id"])
    chat_state = get_chat_state(item['chat_id'])
    global_keyboards_info = json.loads(chat_state.get("global_keyboards_info") or '{}')
    global_keyboards_info.update(
        {
            keyboard_id: {
                "keyboard_name": "routes_keyboard",
            }
        }
    )
    chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})

    update_chat_state(chat_state)
