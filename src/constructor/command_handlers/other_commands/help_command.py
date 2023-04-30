from src.constructor.bot_response import respond_with_text


def handler(data: dict, chat_state: dict):
    respond_with_text(construct_help_message(), data["message"]["chat"]["id"], "markdown")


description_by_command = {
    "register": "Registers user account in the application. Make sure to have your wallet details around.",
    "login": "Logs the user into the application.",
    "update_password": "Updates the password of user's account. Requires old password.",
    "update_wallet_info": "Updates user's wallet details.",
    "delete_account": "Deletes user account. Only possible if any associated routes are deleted/do not exist.",
    "add_vehicle": "Registers a new vehicle under user's account. Only accepts Azerbaijani plate numbers for now.",
    "delete_vehicle": "Deletes previously registered vehicle.",
    "show_vehicles": "Shows all vehicles registered by the user.",
    "create_route": "Starts route creation process. User is expected to have a vehicle registered already.",
    "delete_route": "Deletes previously created route. The route should be inactive/not joined by any passengers yet.",
    "end_route": "Starts route completion process. Is determined using the democratic voting system.",
    "start_route": "Starts route initialization process. Is determined using the democratic voting system.",
    "join_route": "Allows to search for routes based on the user preferences. User can join using the indexed buttons.",
    "leave_route": "Leaves previously joined route. Refunds the booking cost to the user.",
    "show_joined_routes": "Shows routes the user has previously joined.",
    "show_my_routes": "Shows routes the user has created.",
    "show_my_rating": "Displays user rating based on the rankings from the previous routes.",
}


def construct_help_message():
    separator = "-"
    message = ""
    for command, description in description_by_command.items():
        message += (style_command(command) + f" {separator} " + description + "\n")
    return message


def style_command(command):
    return f"*/{command}*"
