import json
from src.database.chat_state import put_chat_state_record

create_route_sequence = [
    "sourceLocation", "destinationLocation", "rideStartTime", "pricePerPerson", "maxPassengerCapacity"
]

step_conf = {
    "sourceLocation": {
        "user_response_key": "location",
        "bot_response_message": "Please share the destination location!"
    },
    "destinationLocation": {
        "user_response_key": "location",
        "bot_response_message": "Please enter the ride start time!"
    },
    "rideStartTime": {
        "user_response_key": "text",
        "bot_response_message": "Please enter the price per each person!"
    },
    "pricePerPerson": {
        "user_response_key": "text",
        "bot_response_message": "Please enter the maximum passenger capacity!"
    },
    "maxPassengerCapacity": {
        "user_response_key": "text",
        "bot_response_message": "Route has successfully been created!"
    },
}


def step_handler(data, state_record):
    state = json.loads(state_record['state'])
    prev_step_index = state['currentStepIndex']
    update_state = handle_prev_step_data(data, prev_step_index)
    new_state = state | update_state
    chat_id = data["message"]["chat"]["id"]
    if prev_step_index == len(create_route_sequence) - 1:
        new_state["currentStepIndex"] = None
        new_state["activeCommand"] = None
        # add_ride(new_state) TODO
        put_chat_state_record(chat_id, {}, {})
        return step_conf[create_route_sequence[prev_step_index]]["bot_response_message"]

    current_step_index = prev_step_index + 1

    new_state["currentStepIndex"] = current_step_index
    put_chat_state_record(chat_id, new_state, {})

    step_name = create_route_sequence[prev_step_index]
    response_message = step_conf[step_name]["bot_response_message"]
    return response_message


def handle_prev_step_data(data, prev_step_index):
    key = create_route_sequence[prev_step_index]
    update_state = {
        key: data["message"][step_conf[key]["user_response_key"]]
    }
    return update_state
