import hashlib
import json
from config.db_config import execute_query
from enums.StatusEnum import StatusEnum


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

def get_amount_of_transaction(connection, cursor, transaction_id):
    query_str = f""" select amount from transactions 
                    where transaction_id = '{transaction_id}' 
                    and status = '{StatusEnum.Initialized.value}' """
    result = execute_query(connection, cursor, query_str)
    amount = 0
    if result:
        amount = result[0][0]

    print(f"\Amount of transaction : {amount} ")
    return amount

def get_amount_of_transaction_for_transfering(connection, cursor, transaction_id):
    query_str = f""" select amount from transactions 
                    where transaction_id = '{transaction_id}' 
                    and status = '{StatusEnum.Confirmed.value}' """
    result = execute_query(connection, cursor, query_str)
    amount = 0
    if result:
        amount = result[0][0]

    print(f"\Amount of transaction : {amount} ")
    return amount

def confirm_transaction_service(connection, cursor, transaction_id, outcome_account_id):
    query_str = f""" UPDATE transactions SET status = '{StatusEnum.Confirmed.value}', 
                    outcome_account_id = '{outcome_account_id}' 
                    WHERE transaction_id = '{transaction_id}'; """
    execute_query(connection, cursor, query_str)

def get_transaction_status(connection, cursor, transaction_id):
    query_str = f""" SELECT status FROM transactions 
                    WHERE transaction_id = '{transaction_id}'
                    """
    result = execute_query(connection, cursor, query_str)
    status = 0
    if result:
        status = result[0][0]

    print(f"\nstatus of transaction : {status} ")
    return status

def get_income_account_id(connection, cursor, transaction_id):
    query_str = f""" select income_account_id from transactions 
                    where transaction_id = '{transaction_id}' """
    result = execute_query(connection, cursor, query_str)
    income_account_id = ''
    if result:
        income_account_id = result[0][0]

    print(f"\nincome_account_id of transaction id {income_account_id}")
    return income_account_id

def create_signature(merchant_id, amount, extraData):
    payload = {
        "merchant_id": merchant_id,
        "amount": amount,
        "extraData": extraData
    }

    return hashlib.md5(json.dumps(payload).encode('utf-8')).hexdigest()