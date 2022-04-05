import uuid

from config.db_config import execute_query


def insert_merchant(connection, cursor, merchant_name, merchant_url):
    api_key = uuid.uuid4()
    query_str = f"INSERT INTO merchants (merchant_url,name, api_key) VALUES ('{merchant_url}', '{merchant_name}', '{api_key}') RETURNING merchant_id;"

    merchant_id = execute_query(connection, cursor, query_str)
    if merchant_id:
        print(f'\nNew merchant id: {merchant_id[0][0]}')
        return merchant_id[0][0], str(api_key)
    else:
        print('\nCan not get merchant id')
        return None, str(api_key)
    
    
