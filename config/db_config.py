import psycopg2


# CONFIG DATABASE
DB_NAME = 'e_wallet'
HOST = "localhost"
USER = "admin"
PASSWORD = "admin"

def get_db_config():
    return DB_NAME, HOST, USER, PASSWORD

def set_up_db_connection(db_name=DB_NAME, host=HOST, user=USER, password=PASSWORD):
    conn = psycopg2.connect(
    host=host,
    database=db_name,
    user=user,
    password=password, 
    port=5432)

    return conn


def connect():
    conn = set_up_db_connection()
    return conn, conn.cursor()


def close_connection(cur):
    cur.close()


def create_table_merchant(connection, cursor):
    table_name = 'merchants'
    sql_str = f"""
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        CREATE TABLE IF NOT EXISTS {table_name} (
            merchant_id uuid DEFAULT uuid_generate_v4 (),
            merchant_url VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            api_key uuid NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone_number VARCHAR(20),
            address VARCHAR(255),
            PRIMARY KEY (merchant_id),
            UNIQUE(api_key)
        )
        """
    cursor.execute(sql_str)
    connection.commit()


def create_table_account(connection, cursor):
    table_name = 'accounts'
    sql_str = f"""
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        CREATE TABLE IF NOT EXISTS {table_name} (
            account_id uuid DEFAULT uuid_generate_v4 (),  
            type VARCHAR(50) NOT NULL,
            balance FLOAT NOT NULL,
            description VARCHAR(255) NOT NULL,
            merchant_id uuid,
            PRIMARY KEY (account_id),
            CONSTRAINT fk_merchant 
                FOREIGN KEY(merchant_id) 
	            REFERENCES merchants(merchant_id) 
        )
        """
    cursor.execute(sql_str)
    connection.commit()

def create_table_transaction(connection, cursor):
    table_name = 'transactions'
    sql_str = f"""
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        CREATE TABLE IF NOT EXISTS {table_name} (
            transaction_id uuid DEFAULT uuid_generate_v4 (),  
            account_id uuid,
            order_id VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL,
            signature VARCHAR(255),
            amount FLOAT NOT NULL,
            extra_data VARCHAR(255) NOT NULL,
            PRIMARY KEY (transaction_id),
            CONSTRAINT fk_account 
                FOREIGN KEY(account_id) 
	            REFERENCES accounts(account_id) 
        )
        """
    cursor.execute(sql_str)
    connection.commit()


def create_all_tables(connection, cursor):
    create_table_merchant(connection, cursor)
    create_table_account(connection, cursor)
    create_table_transaction(connection, cursor)

def execute_query(connection, cursor, query_str):
    cursor.execute(query_str)
    connection.commit()

    if cursor.description == None:
        return None
    else: 
        result = cursor.fetchall()
        return result

def is_table_existed(connection, cursor, table_name):
    query_str = f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE  table_schema = 'public' AND table_name = '{table_name}');"
    is_existed = execute_query(connection, cursor, query_str)[0][0]

    return is_existed
