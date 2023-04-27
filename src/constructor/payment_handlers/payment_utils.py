import json

from web3 import Web3

from src.constructor.web3_utils import send_transaction_to_contract, get_base_wallet_info, call_view_contract_method
from src.database.eth_transactions import put_transaction_request
from src.database.user_info import get_user_info_record

contract_name = "payment"


def deposit_to_contract(username: str, amount: float, chat_id: int, additional_information: dict):
    function_name = "deposit"

    wallet_info = get_user_info_record(username=username)
    tx_hash = send_transaction_to_contract(
        wallet_info=wallet_info,
        contract_name=contract_name,
        function_name=function_name,
        function_args=[],
        extra_fields={
            "amount": Web3.toWei(amount, 'finney'),
        }
    )

    # save to db
    put_transaction_request(
        tx_hash=tx_hash,
        chat_id=chat_id,
        extra_fields={
            "username": username,
            "function_name": function_name,
            "contract_name": contract_name,
            "amount": Web3.toWei(amount, 'finney'),
            "additional_information": json.dumps(additional_information),
        },
    )


def transfer(passengers: list[str], username: str, amount: float, chat_id: int):
    function_name = "processPayment"

    base_wallet_info = get_base_wallet_info()
    receiver_wallet_info = get_user_info_record(username=username)
    tx_hash = send_transaction_to_contract(
        wallet_info=base_wallet_info,
        contract_name=contract_name,
        function_name=function_name,
        function_args=[passengers, receiver_wallet_info['wallet_address'], Web3.toWei(amount, 'finney')],
    )

    # save to db
    put_transaction_request(
        tx_hash=tx_hash,
        chat_id=chat_id,
        extra_fields={
            "username": username,
            "function_name": function_name,
            "contract_name": contract_name,
            "amount": Web3.toWei(amount, 'finney')
        }
    )


def withdraw(username: str, amount: float, chat_id: int):
    function_name = "withdraw"

    wallet_info = get_user_info_record(username=username)
    tx_hash = send_transaction_to_contract(
        wallet_info=wallet_info,
        contract_name=contract_name,
        function_name=function_name,
        function_args=[Web3.toWei(amount, 'finney')],
    )

    # save to db
    put_transaction_request(
        tx_hash=tx_hash,
        chat_id=chat_id,
        extra_fields={
            "username": username,
            "function_name": function_name,
            "contract_name": contract_name,
            "amount": Web3.toWei(amount, 'finney')
        }
    )


def balance_of(username: str):
    function_name = "balanceOf"

    wallet_info = get_user_info_record(username=username)
    response = call_view_contract_method(
        contract_name=contract_name,
        function_name=function_name,
        function_args=[wallet_info['wallet_address']]
    )

    return response
