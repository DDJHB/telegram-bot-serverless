
from src.constructor.web3_utils import send_transaction_to_contract


def handler(data):
    username = data["message"]["chat"]["username"]
    message = str(data["message"]["text"])
    if " " not in message:
        return f"Please enter the password with /register xxxx command!"

    user_password = message.split(" ")[1]
    response = register_user(username=username, password=user_password)
    return response


def register_user(username: str, password: str) -> str:
    response = send_transaction_to_contract(
        contract_path="smart_contract_abis/onboarding_contract_abi.json",
        function_name="registerUser",
        function_args={
          "username": username,
          "password": password,
        },
    )

    # verify operation success
    # TODO implement registration verification
    if response:
        ...

    # respond to user
    return "User has been successfully registered"
