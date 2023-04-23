import json

from src.constructor.web3_utils import send_transaction_to_contract, call_view_contract_method
from src.constructor.services.vehicle import Vehicle
from src.database.eth_transactions import put_transaction_request
from src.database.user_info import get_wallet_info_record

contract_name = "vehicle"


def get_user_vehicles(username: str):
    function_name = "getUserVehicles"

    response = call_view_contract_method(
        contract_name=contract_name,
        function_name=function_name,
        function_args=[username]
    )

    return response


def get_user_vehicle(username: str, index: int):
    function_name = "getUserVehicle"

    response = call_view_contract_method(
        contract_name=contract_name,
        function_name=function_name,
        function_args=[username, index]
    )

    return response


def add_user_vehicle(username: str, vehicle: Vehicle, chat_id: int):
    function_name = "addVehicle"
    vehicle_tuple = vehicle.get_tuple()

    wallet_info = get_wallet_info_record(username)

    tx_hash = send_transaction_to_contract(
        wallet_info=wallet_info,
        contract_name=contract_name,
        function_name=function_name,
        function_args=[username, vehicle_tuple],
    )

    # save to db
    put_transaction_request(
        tx_hash=tx_hash,
        chat_id=chat_id,
        extra_fields={
            "username": username,
            "function_name": function_name,
            "contract_name": contract_name,
            "function_args": json.dumps({}),
        }
    )


def update_user_vehicle(username: str, index: int, vehicle: Vehicle, chat_id: int):
    function_name = "updateVehicle"
    vehicle_tuple = vehicle.get_tuple()

    wallet_info = get_wallet_info_record(username=username)

    tx_hash = send_transaction_to_contract(
        wallet_info=wallet_info,
        contract_name=contract_name,
        function_name=function_name,
        function_args=[username, index, vehicle_tuple],
    )

    # save to db
    put_transaction_request(
        tx_hash=tx_hash,
        chat_id=chat_id,
        extra_fields={
            "username": username,
            "function_name": function_name,
            "contract_name": contract_name,
            "function_args": json.dumps({})
        }
    )


def remove_user_vehicle(username: str, index: int, vehicle: Vehicle, chat_id: int):
    function_name = "deleteVehicle"

    wallet_info = get_wallet_info_record(username=username)
    tx_hash = send_transaction_to_contract(
        wallet_info=wallet_info,
        contract_name=contract_name,
        function_name=function_name,
        function_args=[username, index],
    )

    # save to db
    put_transaction_request(
        tx_hash=tx_hash,
        chat_id=chat_id,
        extra_fields={
            "username": username,
            "function_name": function_name,
            "contract_name": contract_name,
            "function_args": json.dumps({})
        }
    )
