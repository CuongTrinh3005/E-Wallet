from sched import scheduler
import socketserver
import psycopg2
from apscheduler.schedulers.background import BackgroundScheduler
from api_handler import APIHandler

from config.db_config import close_connection, connect, create_all_tables
from services.transaction_services import check_transaction_expire


if __name__ == "__main__":
    try:
        connection, cursor = connect()
        if cursor == None:
            print("\nConnect failed!\n")
        else:
            print("\nConnect successfully!\n")

        print("Checking for creating tables")
        create_all_tables(connection, cursor)

        # Create scheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(lambda:check_transaction_expire(connection, cursor), 'interval', seconds=5)
        scheduler.start()

        PORT = 8000
        # Create an object of the above class
        my_server = socketserver.TCPServer(("0.0.0.0", PORT), APIHandler)
        # Star the server
        print(f"Server started at {PORT}")
        my_server.serve_forever()
    except (Exception, psycopg2.Error) as error:
        print("Error while processing data from PostgreSQL", error)
    finally:
        close_connection(cursor)
        print("\nClose connection\n")