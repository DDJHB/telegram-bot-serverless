import os
import json

from src.constructor.web3_utils import send_transaction_to_contract
from src.database.eth_transactions import put_transaction_request


def handler(data):
    username = data["message"]["chat"]["username"]
    message = str(data["message"]["text"])
    chat_id = data["message"]["chat"]["id"]
    if " " not in message:
        return f"Please enter the password with /register xxxx command!"

    user_password = message.split(" ")[1]
    response = register_user(username=username, password=user_password, chat_id=chat_id)

    # respond to user
    return response


def register_user(username: str, password: str, chat_id: str) -> str:
    function_name = "registerUser"
    contract_name = "onboarding_contract_abi"
    function_args = {
      "username": username,
      "password": password,
    }

    tx_hash = send_transaction_to_contract(
        contract_path=os.path.join("smart_contract_abis", f"{contract_name}.json"),
        function_name=function_name,
        function_args=[username, password]
    )

    # save to db
    put_transaction_request(
        tx_hash=tx_hash,
        chat_id=chat_id,
        extra_fields={
            "username": username,
            "function_name": function_name,
            "contract_name": contract_name,
            "function_args": json.dumps(function_args),
        }
    )

    return "Registering user..."
