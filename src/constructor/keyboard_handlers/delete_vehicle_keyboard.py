from src.constructor.services.vehicle_crud import remove_user_vehicle

def handler(keyboard_id, callback_query, chat_state):
    username = callback_query['from']['username']
    vehicle_id = callback_query['data']
    remove_user_vehicle(username, vehicle_id)
