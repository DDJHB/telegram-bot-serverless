from src.constructor.bot_response import respond_with_text


def handler(data: dict, chat_state: dict):
    respond_with_text(construct_help_message(), data["message"]["chat"]["id"], "markdown")


def construct_help_message():
    return f"*/register*: registers user in the application by prompting user details\n" \
           f"*/login password*: logs in the user. User password shall be inputted in place of the password word\n" \
           f"*/updatePassword*: updates the user password\n" \
           f"*/updateWalletInfo*: updates the user wallet account information\n" \
           f"*/addVehicle*: adds a vehicle for the user by prompting car details\n" \
           f"*/deleteVehicle*: deletes a vehicle for the user\n" \
           f"*/showVehicles*: shows the vehicles of the user\n" \
           f"*/createRoute*: creates a route for the driver by prompting route details\n" \
           f"*/deleteRoute*: deletes a route of the driver\n" \
           f"*/startRoute*:  attempts to start the route initiated by the driver by invoking the passenger approval " \
           f"and ranking\n" \
           f"*/endRoute*: attempts to end the route initiated by the driver by invoking the passenger approval and " \
           f"ranking\n" \
           f"*/showMyRoutes*: shows the routes of the driver\n" \
           f"*/joinRoute*: joins the passenger to the route\n" \
           f"*/showRating*: shows the rating of the driver"
