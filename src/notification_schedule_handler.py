from src.constructor.bot_response import respond_with_text
from src.constructor.decorators import standard_api_handler
from src.database.routes import get_routes_by_start_time


@standard_api_handler
def handler(event, context):
    try:

        routes_1_hour = get_routes_by_start_time(1)
        routes_24_hour = get_routes_by_start_time(24)

        for item in routes_1_hour.get('Items', []):
            respond_with_text(f"One hour left till {item['route_name']} route!", item['chat_id'])

        for item in routes_24_hour.get('Items', []):
            respond_with_text(f"One day left till {item['route_name']} route!", item['chat_id'])

        return {'statusCode': 200}
    except Exception as error:
        print(error)
        return {'statusCode': 200}
