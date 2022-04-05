import jwt
import datetime

from config.db_config import execute_query


def insert_account(connection, cursor, type, description, merchant_id):
    query_str = f"INSERT INTO accounts (type, description, merchant_id) VALUES ('{type}', '{description}', '{merchant_id}') RETURNING account_id;"

    account_id = execute_query(connection, cursor, query_str)
    if account_id:
        print(f'\nNew merchant id: {account_id[0][0]}')
        return account_id[0][0]
    else:
        print('\nCan not get merchant id')
        return None
    
def insert_account_without_merchant(connection, cursor, type, description, merchant_id):
    query_str = f"INSERT INTO accounts (type, description) VALUES ('{type}', '{description}') RETURNING account_id;"

    account_id = execute_query(connection, cursor, query_str)
    if account_id:
        print(f'\nNew merchant id: {account_id[0][0]}')
        return account_id[0][0]
    else:
        print('\nCan not get merchant id')
        return None

def generate_jwt(account_id):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=5),
            'iat': datetime.datetime.utcnow(),
            'sub': account_id
        }
        key = "Cuong"
        return jwt.encode(
            payload,
            key,
            algorithm='HS256'
        )
    except Exception as e:
        return e
