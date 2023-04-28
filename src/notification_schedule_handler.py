from src.constructor.bot_response import respond_with_text, respond_with_inline_keyboard
from src.constructor.decorators import standard_api_handler
from src.constructor.services.tg_keyboard import build_view_keyboard
from src.database.routes import get_routes_by_start_time


def handler(event, context):
    try:
        routes_1_hour = get_routes_by_start_time(1)
        routes_24_hour = get_routes_by_start_time(24)
        print(routes_1_hour, routes_24_hour)

        for item in routes_1_hour.get('Items', []):
            keyboard_def = build_view_keyboard([item])
            tg_response = respond_with_inline_keyboard(
                parent_message=f"One hour left till {item['route_name']} route!",
                keyboard_definition=keyboard_def,
                chat_id=item['chat_id']
            )

        for item in routes_24_hour.get('Items', []):
            keyboard_def = build_view_keyboard([item])
            tg_response = respond_with_inline_keyboard(
                parent_message=f"One day left till {item['route_name']} route!",
                keyboard_definition=keyboard_def,
                chat_id=item['chat_id']
            )

        return {'statusCode': 200}
    except Exception as error:
        print(error)
        return {'statusCode': 200}
