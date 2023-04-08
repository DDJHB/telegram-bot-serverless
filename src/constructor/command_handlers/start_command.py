
def handler(data: dict, chat_state: dict):
    first_name = data["message"]["chat"]["first_name"]
    return f"Hello {first_name}"
