from unittest import result
import jwt
import datetime

from config.db_config import execute_query
from enums.StatusEnum import StatusEnum
from enums.TypeEnum import TypeEnum


key = "Cuong"

def insert_account(connection, cursor, type, description, merchant_id):
    query_str = f"INSERT INTO accounts (type, description, merchant_id) VALUES ('{type}', '{description}', '{merchant_id}') RETURNING account_id;"

    account_id = execute_query(connection, cursor, query_str)
    if account_id:
        print(f'\nNew account id: {account_id[0][0]}')
        return account_id[0][0]
    else:
        print('\nCan not get account id')
        return None
    
def insert_account_without_merchant(connection, cursor, type, description):
    query_str = f"INSERT INTO accounts (type, description) VALUES ('{type}', '{description}') RETURNING account_id;"

    account_id = execute_query(connection, cursor, query_str)
    if account_id:
        print(f'\nNew account id: {account_id[0][0]}')
        return account_id[0][0]
    else:
        print('\nCan not get account id')
        return None


def check_valid_acc_type(connection, cursor, account_id, type_to_check = TypeEnum.Issuer.value):
    """ Return 1 indicating True and 0 for False counterpart """
    query_str = f"SELECT EXISTS (SELECT account_id FROM accounts WHERE account_id='{account_id}' and type = '{type_to_check}')::int "
    print(f"Query String: {query_str}\n")
    is_valid = execute_query(connection, cursor, query_str)

    print("\nValid Account: ", is_valid[0][0])
    return is_valid[0][0]

def topup(connection, cursor, account_id, amount):
    query_str = f"UPDATE accounts SET balance = balance + {amount} WHERE account_id = '{account_id}';"
    execute_query(connection, cursor, query_str)


def get_balance_of_account(connection, cursor, account_id):
    query_str = f""" select balance from accounts 
                    where account_id = '{account_id}' """
    result = execute_query(connection, cursor, query_str)
    balance = 0
    if result:
        balance = result[0][0]

    print(f"\Balance of transaction id {balance}: ")
    return balance

def transfer(connection, cursor, transaction_id, income_account_id, outcome_account_id, amount):
    query_str = f""" BEGIN; 
                    UPDATE transactions SET status = '{StatusEnum.Verified.value}' 
                        WHERE transaction_id = '{transaction_id}' and status = '{StatusEnum.Confirmed.value}';
                    UPDATE accounts SET balance = balance - {amount} 
                        WHERE account_id = '{outcome_account_id}'; 
                    UPDATE accounts SET balance = balance + {amount} 
                        WHERE account_id = '{income_account_id}'; 
                    COMMIT; """
    execute_query(connection, cursor, query_str)

def generate_jwt(account_id):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=5),
            'iat': datetime.datetime.utcnow(),
            'sub': account_id
        }
        
        return jwt.encode(
            payload,
            key,
            algorithm='HS256'
        )
    except Exception as e:
        return e

def decode_jwt(token):
    """ Token will be decoded into account id """
    try:
        payload = jwt.decode(token, key, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please try again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please try again.'