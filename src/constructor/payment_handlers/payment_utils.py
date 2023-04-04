from web3 import Web3

from src.constructor.web3_utils import send_transaction_to_contract, get_base_wallet_info, call_view_contract_method
from src.database.eth_transactions import put_transaction_request
from src.database.user_info import get_wallet_info_record

contract_name = "payment"


def deposit(username: str, amount: float, chat_id: int):
    function_name = "deposit"

    wallet_info = get_wallet_info_record(username=username)
    tx_hash = send_transaction_to_contract(
        wallet_info=wallet_info,
        contract_name=contract_name,
        function_name=function_name,
        function_args=[],
        extra_fields={
            "amount": Web3.toWei(amount, 'ether'),
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
            "amount": Web3.toWei(amount, 'ether')
        }
    )


def transfer(username: str, amount: float, chat_id: int):
    function_name = "processPayment"

    base_wallet_info = get_base_wallet_info()
    receiver_wallet_info = get_wallet_info_record(username=username)
    tx_hash = send_transaction_to_contract(
        wallet_info=base_wallet_info,
        contract_name=contract_name,
        function_name=function_name,
        function_args=[receiver_wallet_info['wallet_address'], Web3.toWei(amount, 'ether')],
    )

    # save to db
    put_transaction_request(
        tx_hash=tx_hash,
        chat_id=chat_id,
        extra_fields={
            "username": username,
            "function_name": function_name,
            "contract_name": contract_name,
            "amount": Web3.toWei(amount, 'ether')
        }
    )


def withdraw(username: str, amount: float, chat_id: int):
    function_name = "withdraw"

    wallet_info = get_wallet_info_record(username=username)
    tx_hash = send_transaction_to_contract(
        wallet_info=wallet_info,
        contract_name=contract_name,
        function_name=function_name,
        function_args=[Web3.toWei(amount, 'ether')],
    )

    # save to db
    put_transaction_request(
        tx_hash=tx_hash,
        chat_id=chat_id,
        extra_fields={
            "username": username,
            "function_name": function_name,
            "contract_name": contract_name,
            "amount": Web3.toWei(amount, 'ether')
        }
    )


def balance_of(username: str):
    function_name = "balanceOf"

    wallet_info = get_wallet_info_record(username=username)
    response = call_view_contract_method(
        contract_name=contract_name,
        function_name=function_name,
        function_args=[wallet_info['wallet_address']]
    )

    return response