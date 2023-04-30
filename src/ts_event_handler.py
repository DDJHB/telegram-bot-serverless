import json
import os

from src.constructor.decorators import standard_api_handler
from src.constructor.web3_utils import process_tx_hash
from src.database.eth_transactions import get_transaction
from src.constructor.bot_response import respond_with_text
from src.constructor.post_transaction_handlers import route_join_post_deposit, route_leave_post_withdraw


@standard_api_handler
def handler(event, context):
    try:
        tx_event_data = event['body']
        tx_hash = tx_event_data['event']['transaction']['hash']
        transaction_data = get_transaction(tx_hash)
        contract_name, function_name = transaction_data["contract_name"], transaction_data["function_name"]

        logs = process_tx_hash(
            tx_hash=tx_hash,
            contract_name=contract_name,
            function_name=function_name,
        )

        if contract_name == "payment":
            if function_name == "deposit":
                route_join_post_deposit.handle_tx_logs(logs, transaction_data)
            elif function_name == "withdraw":
                route_leave_post_withdraw.handle_tx_logs(logs, transaction_data)

        elif logs[0]['args'].get('status') is not None:
            message = logs[0]['args']['message']

            respond_with_text(message, transaction_data["chat_id"])

        return {'statusCode': 200}
    except Exception as error:
        print(error)
        return {'statusCode': 200}
