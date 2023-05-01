import os
import json

from web3 import Web3

alchemy_url = os.getenv("ALCHEMY_API_URL")
w3 = Web3(Web3.HTTPProvider(alchemy_url))
onboarding_contract_address = os.getenv("ONBOARDING_CONTRACT_ADDRESS")
payment_contract_address = os.getenv("PAYMENT_CONTRACT_ADDRESS")
private_key = os.getenv("WALLET_PRIVATE_KEY")
wallet_address = os.getenv("WALLET_ADDRESS")
vehicle_contract_address = os.getenv("VEHICLE_MANAGEMENT_SERVICE_ADDRESS")

contract_addresses = {
    "onboarding": onboarding_contract_address,
    "payment": payment_contract_address,
    "vehicle": vehicle_contract_address,
}

event_processing = {
    "registerUser": "RegistrationInfo",
    "deposit": "Deposit",
    "processPayment": "Transfer",
    "withdraw": "Withdraw",
    "changePassword": "PasswordChangeInfo",
    "deleteAccount": "AccountDeletionInfo",
    "addVehicle": "AddVehicleInformation",
    "deleteVehicle": "DeleteVehicleInformation",
    "deleteAllVehicles": "DeleteVehiclesInformation",
}


def get_base_wallet_info():
    return {
        "wallet_address": wallet_address,
        "private_key": private_key
    }


def get_contract_info(contract_name: str):
    contract_abi_path = os.path.join("smart_contract_abis", f"{contract_name}_contract_abi.json")

    # connecting to contract
    with open(contract_abi_path, 'r') as f:
        abi_str = f.read()

    abi = json.loads(abi_str)
    contract = w3.eth.contract(address=contract_addresses[contract_name], abi=abi)

    return contract


def send_transaction_to_contract(wallet_info: dict, contract_name: str, function_name: str, function_args: list,
                                 extra_fields: dict = {}) -> str:
    contract = get_contract_info(contract_name)

    # establish function and transaction parameters
    function = contract.functions[function_name]
    nonce = w3.eth.getTransactionCount(wallet_info['wallet_address'])

    tx_params = {
        'from': wallet_info['wallet_address'],
        'gas': 500000,
        'gasPrice': w3.toWei('5000', 'wei'),
        'nonce': nonce
    }

    # for payment transactions
    if extra_fields.get('amount') is not None:
        tx_params.update({'value': extra_fields['amount']})

    tx = function(*function_args).buildTransaction(tx_params)

    # sign and send transaction
    signed_tx = w3.eth.account.signTransaction(tx, private_key=wallet_info['private_key'])
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    return w3.toHex(tx_hash)


def call_view_contract_method(contract_name: str, function_name: str, function_args: list):
    contract = get_contract_info(contract_name)
    function = contract.functions[function_name]
    response = function(*function_args).call()
    return response


def process_tx_hash(tx_hash: str, contract_name: str, function_name: str) -> dict:
    contract = get_contract_info(contract_name)

    tx_hash_encoded = bytes.fromhex(tx_hash[2:])  # remove 0x
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash_encoded)

    return contract.events[event_processing[function_name]]().processReceipt(receipt)
