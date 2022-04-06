import hashlib
import json
from config.db_config import execute_query


def insert_new_transaction(connection, cursor, merchant_id, income_account_id, amount, extra_data, signature, status):
    query_str = f"""INSERT INTO transactions (merchant_id, income_account_id, amount, extra_data, signature, status) 
                VALUES ('{merchant_id}', '{income_account_id}', {amount}, '{extra_data}', '{signature}', '{status}') 
                RETURNING transaction_id;"""

    transaction_id = execute_query(connection, cursor, query_str)
    if transaction_id:
        print(f'\nNew transaction id: {transaction_id[0][0]}')
        return transaction_id[0][0]
    else:
        print('\nCan not get transaction id')
        return None

def update_transaction_status(connection, cursor, transaction_id, status):
    query_str = f"UPDATE transactions SET status = '{status}' WHERE transaction_id = '{transaction_id}';"
    execute_query(connection, cursor, query_str)

def check_transaction_exist(connection, cursor, transaction_id):
    query_str = f"SELECT EXISTS (SELECT transaction_id FROM transactions WHERE transaction_id='{transaction_id}')::int "
    is_existed = execute_query(connection, cursor, query_str)

    print("\nExisted Transaction: ", is_existed[0][0])
    return is_existed[0][0]


def create_signature(merchant_id, amount, extraData):
    payload = {
        "merchant_id": merchant_id,
        "amount": amount,
        "extraData": extraData
    }

    return hashlib.md5(json.dumps(payload).encode('utf-8')).hexdigest()