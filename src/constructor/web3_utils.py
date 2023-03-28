import os
import json

from web3 import Web3


alchemy_url = os.getenv("ALCHEMY_API_URL")
w3 = Web3(Web3.HTTPProvider(alchemy_url))
contract_address = os.getenv("SMART_CONTRACT_ADDRESS")
private_key = os.getenv("WALLET_PRIVATE_KEY")
wallet_address = os.getenv("WALLET_ADDRESS")


def send_transaction_to_contract(contract_path: str, function_name: str, function_args: list) -> str:
    # connecting to contract
    with open(contract_path, 'r') as f:
        abi_str = f.read()

    abi = json.loads(abi_str)
    contract = w3.eth.contract(address=contract_address, abi=abi)

    # establish function and transaction parameters
    function = contract.functions[function_name]
    nonce = w3.eth.getTransactionCount(wallet_address)

    tx_params = {
        'from': wallet_address,
        'gas': 200000,
        'gasPrice': w3.toWei('200', 'gwei'),
        'nonce': nonce
    }

    tx = function(*function_args).buildTransaction(tx_params)

    # sign and send transaction
    signed_tx = w3.eth.account.signTransaction(tx, private_key=private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    return w3.toHex(tx_hash)


def call_view_contract_method(contract_path: str, function_name: str, function_args: list):
    with open(contract_path, mode="r") as f:
        data = f.read()
    abi = json.loads(data)
    contract = w3.eth.contract(address=contract_address, abi=abi)
    function = contract.functions[function_name]
    print(*function_args)
    login = function(*function_args).call()
    print(login)
    return login


def process_tx_hash(tx_hash: str, contract_path: str) -> dict:
    with open(contract_path, 'r') as f:
        abi_str = f.read()

    abi = json.loads(abi_str)
    contract = w3.eth.contract(address=contract_address, abi=abi)

    tx_hash_encoded = bytes.fromhex(tx_hash[2:])   # remove 0x
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash_encoded)

    return contract.events.RegistrationInfo().processReceipt(receipt)