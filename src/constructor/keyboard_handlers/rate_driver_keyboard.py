from src.constructor.bot_response import respond_with_text
from src.constructor.services.vehicle_crud import remove_user_vehicle
from src.database.routes import get_route_by_id
from src.database.user_info import get_user_info_record, put_user_info_record


def handler(keyboard_id, callback_query, chat_state):
    chat_id = callback_query['message']['chat']['id']
    route_id = callback_query['data']
    rating = float(callback_query['message'])

    route = get_route_by_id(route_id)
    driver = route['owner_username']

    cur_info = get_user_info_record(driver)

    new_rating = (cur_info.get('rating', 0.0) * cur_info.get('raters_num', 0) + rating)/(cur_info.get('raters_num', 0) + 1)

    put_user_info_record(
        username=driver,
        wallet_address=cur_info['wallet_address'],
        private_key=cur_info['private_key'],
        rating=new_rating,
        raters_num=cur_info.get('raters_num', 0) + 1,
        extra_fields={}
    )

    respond_with_text(f"Rated {driver} {rating}\U00002B50", chat_id)
