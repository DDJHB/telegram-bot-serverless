
from src.constructor.bot_response import respond_with_text


def handler(data: dict, chat_state: dict):
    first_name = data["message"]["chat"]["first_name"]
    respond_with_text(f"Hello {first_name}", chat_state['chat_id'])
