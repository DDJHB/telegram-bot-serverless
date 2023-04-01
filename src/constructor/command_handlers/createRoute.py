
from src.database.chat_state import put_chat_state_record


def handler(data):
    chat_id = data["message"]["chat"]["id"]
    state = {
        "activeCommand": "createRoute",
        "currentStepIndex": 0,
    }
    put_chat_state_record(
        chat_id,
        state,
        {}
    )
    return "Please share the starting location!"
