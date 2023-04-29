import random

from src.constructor.bot_response import respond_with_text


def handler(data: dict, chat_state: dict):
    respond_with_text(str(random.randint(0, 100)), chat_state.get('chat_id'))
