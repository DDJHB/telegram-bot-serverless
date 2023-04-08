import random


def handler(data: dict, chat_state: dict):
    return str(random.randint(0, 100))
