from datetime import datetime
import hashlib
import json
from config.db_config import execute_query
from enums.StatusEnum import StatusEnum
import requests
import json


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


def update_order_status(data):
    headers = {
        "Content-Type": "application/json; charset=utf-8"
        }
    res = requests.post(
        url='http://127.0.0.1:5000/order/change-order-status', 
        data=json.dumps(data), 
        headers=headers)
    
    return res.status_code

def get_income_account_id(connection, cursor, transaction_id):
    query_str = f""" select income_account_id from transactions 
                    where transaction_id = '{transaction_id}' """
    result = execute_query(connection, cursor, query_str)
    income_account_id = ''
    if result:
        income_account_id = result[0][0]

    print(f"\nincome_account_id of transaction id {income_account_id}")
    return income_account_id

def get_extra_data(connection, cursor, transaction_id):
    query_str = f""" select extra_data from transactions 
                    where transaction_id = '{transaction_id}' """
    result = execute_query(connection, cursor, query_str)
    extra_data = ''
    if result:
        extra_data = result[0][0]

    print(f"\nextra_data of transaction id {extra_data}")
    return extra_data

def create_signature(merchant_id, amount, extraData):
    payload = {
        "merchant_id": merchant_id,
        "amount": amount,
        "extraData": extraData
    }

    return hashlib.md5(json.dumps(payload).encode('utf-8')).hexdigest()

def check_transaction_expire(conn, cur):
    # get list transaction
    command_select = f""" SELECT transaction_id, created_at, extra_data 
                        FROM transactions 
                        WHERE status!='{StatusEnum.Completed.value}' 
                        AND status!='{StatusEnum.Canceled.value}' 
                        AND status!='{StatusEnum.Failed.value}' 
                        AND status!='{StatusEnum.Expired.value}'  """

    cur.execute(command_select)
    trans=cur.fetchall()
    if(len(trans)<=0):
        print ("no transaction found !!!")
        return

    for tran in trans:
        # _datetime=datetime.strptime(tran[1],"YYYY-MM-DD HH:MM:SS")
        _datetime=tran[1]
        distance = datetime.now() - _datetime
        a_minute = 60
        if distance.total_seconds() > (5*a_minute):
        # update transaction staus to expire
            # call api update order status
            data = {
                "order_id": tran[2],
                "status": StatusEnum.Expired.value
            }
            status_code = update_order_status(data=data)  
            if status_code == 200:
                command_update = f"""UPDATE transactions 
                                    SET status='{StatusEnum.Expired.value}' 
                                    WHERE transaction_id='{tran[0]}' """

                cur.execute(command_update)
                conn.commit()

                print(f"\nUpdate status for transaction id = {tran[0]} - order id = {tran[2]}")