import os

from src.constructor.decorators import standard_api_handler
from src.constructor.web3_utils import process_tx_hash
from src.database.eth_transactions import get_transaction
from src.constructor.bot_response import respond_with_text


@standard_api_handler
def handler(event, context):
    try:
        tx_event_data = event['body']
        tx_hash = tx_event_data['event']['transaction']['hash']
        transaction_data = get_transaction(tx_hash)

        logs = process_tx_hash(
            tx_hash=tx_hash,
            contract_path=os.path.join("smart_contract_abis", f"{transaction_data['contract_name']}.json")
        )

        if logs[0]['args']['got_registered']:
            message = f"{transaction_data['username']}, you have been registered successfully!"
        else:
            message = f"You have previously been registered. Please, login into your account to proceed!"

        respond_with_text(message, transaction_data["chat_id"])
        return {'statusCode': 200}
    except Exception as error:
        print(error)
        return {'statusCode': 200}
