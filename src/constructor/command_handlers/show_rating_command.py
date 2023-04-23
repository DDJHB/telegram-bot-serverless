from src.constructor.bot_response import respond_with_text
from src.database.user_info import get_user_info_record


def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    username = data['message']['from']['username']
    user_info = get_user_info_record(username)
    rating = user_info.get('rating', 0.0)
    raters_num = user_info.get('raters_num', 0)

    if not raters_num:
        respond_with_text("You have not been rated yet!", chat_id)

    else:
        respond_with_text(f"Your current rating is {round(rating, 2)}\U00002B50 based on {raters_num} votes!", chat_id)

