
from src.constructor.services.tg_keyboard import handle_navigation_buttons, handle_route_info_button
from src.database.routes import get_user_routes, get_route_by_id
from src.constructor.payment_handlers.payment_utils import withdraw, balance_of
from src.constructor.bot_response import respond_with_text


def handler(keyboard_id, callback_query, chat_state):
    button_info = callback_query["data"]
    username = callback_query["from"]["username"]
    chat_id = callback_query["from"]["id"]

    if any(button_info.startswith(button_name) for button_name in ["next", "back"]):
        handle_navigation_buttons(
            keyboard_id=keyboard_id,
            callback_query=callback_query,
            chat_state=chat_state,
            query_method=get_user_routes,
            query_args={"username": username, "is_passenger": True},
            extend_with_indices=False,
        )
        return

    if button_info.startswith("info"):
        route = get_route_by_id(button_info.split("+")[-1])
        handle_route_info_button(route, chat_id)
        return

    route = get_route_by_id(button_info)
    if route["has_started"]:
        respond_with_text("Can not leave started route!", chat_id)

    respond_with_text(f"Leaving route {route['route_name']}...", chat_id)
    try:
        withdraw(
            username=username,
            amount=route["pricePerPerson"],
            chat_id=chat_id,
            additional_information={
                "route_id": route["route_id"],
                "username": username,
                "chat_id": chat_id,
                "keyboard_id": keyboard_id,
            }
        )
    except:
        respond_with_text("Could not leave the route, error with refund", chat_id)
