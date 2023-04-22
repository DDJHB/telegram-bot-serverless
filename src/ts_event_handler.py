import json
import os

from src.constructor.decorators import standard_api_handler
from src.constructor.web3_utils import process_tx_hash
from src.database.chat_state import update_chat_state
from src.database.eth_transactions import get_transaction
from src.constructor.bot_response import respond_with_text


@standard_api_handler
def handler(event, context):
    try:
        tx_event_data = event['body']
        tx_hash = tx_event_data['event']['transaction']['hash']
        transaction_data = get_transaction(tx_hash)
        function_name = transaction_data['function_name']

        logs = process_tx_hash(
            tx_hash=tx_hash,
            contract_name=transaction_data['contract_name'],
            function_name=function_name,
        )

        if logs[0]['args'].get('status') is not None:
            message = logs[0]['args']['message']

            respond_with_text(message, transaction_data["chat_id"])

        return {'statusCode': 200}
    except Exception as error:
        print(error)
        return {'statusCode': 200}
