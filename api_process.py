import json
from http import HTTPStatus
import time

from decorators.expired_decorator import timeout

from enums.StatusEnum import StatusEnum
from enums.TypeEnum import TypeEnum
from services.account_services import check_valid_acc_type, decode_jwt
from services.transaction_services import check_transaction_exist, create_signature, insert_new_transaction, update_transaction_status
from decorators.expired_decorator import TimeoutError


def dump_response(dict_data):
    output_json = json.dumps(dict_data)
    return output_json.encode('utf-8')

def sleep_print():
    print("Start")
    for i in range(1,10):
        time.sleep(1)
        print("%d seconds have passed" % i)

@timeout(5)
# @token_required
def test(obj):
    obj.send_response(HTTPStatus.OK)
    obj.send_header("Content-Type", "application/json")
    obj.end_headers()

    sleep_print()
    response = {
        "status": "OK",
        "message": "Get all merchants"
    }
    obj.wfile.write(dump_response(response))

@timeout(5)
def create_transaction(obj, connection, cursor, merchant_id, amount, extraData, signature):
    try:
        jwt_token = obj.headers['Authorization']
        income_account_id = decode_jwt(jwt_token)

        # connection, cursor = get_connection_and_cursor()
        is_merchant_account = check_valid_acc_type(connection, cursor, income_account_id, TypeEnum.Merchant.value)
        transaction_id = ''
        if is_merchant_account == 1:
            if amount > 0:
                # Assume error in creating process
                # x = 2/0

                # Assume error timeout in creating process
                # sleep_print()

                transaction_id = insert_new_transaction(connection, cursor, merchant_id, income_account_id, 
                                                        amount, extraData, signature, StatusEnum.Initialized.value)

                # sleep_print()
                
                # - response -
                obj.send_response(200)
                obj.send_header('Content-type', 'text/json')
                obj.end_headers()
                
                output_data = {
                    "transactionId": transaction_id,
                    "merchantId": merchant_id,
                    "incomeAccount": income_account_id,
                    "outcomeAccount": "",
                    "amount": amount,
                    "extraData": extraData,
                    "signature": signature,
                    "status": "INITIALIZED"
                }
            else:
                obj.send_response(400)
                obj.send_header('Content-type', 'text/json')
                obj.end_headers()
                
                output_data = {"message": "Amount must be larger than 0!"}
        else:
            obj.send_response(400)
            obj.send_header('Content-type', 'text/json')
            obj.end_headers()
            output_data = {"message": "You need to be a merchant for creating transaction!"}

        obj.wfile.write(dump_response(output_data))
    except TimeoutError:
        # If expired create new failed transaction
        if transaction_id != '':
            is_existed = check_transaction_exist(connection, cursor, transaction_id)
            if is_existed == 0:
                transaction_id = insert_new_transaction(connection, cursor, merchant_id, income_account_id, 
                                                amount, extraData, signature, StatusEnum.Expired.value)
            else:
                update_transaction_status(connection, cursor, transaction_id, StatusEnum.Expired.value)

        obj.send_response(200)
        obj.send_header('Content-type', 'text/json')
        obj.end_headers()
        
        output_data = {
            "transactionId": transaction_id,
            "merchantId": merchant_id,
            "incomeAccount": income_account_id,
            "outcomeAccount": "",
            "amount": amount,
            "extraData": extraData,
            "signature": signature,
            "status": "EXPIRED",
            "message": "Transaction is exceed the limit time!"
        }
        obj.wfile.write(dump_response(output_data))
    except Exception as ex:
        print("Exception: ", ex)
        transaction_id = insert_new_transaction(connection, cursor, merchant_id, income_account_id, 
                                                        amount, extraData, signature, StatusEnum.Failed.value)
        obj.send_response(200)
        obj.send_header('Content-type', 'text/json')
        obj.end_headers()
        
        output_data = {
            "transactionId": transaction_id,
            "merchantId": merchant_id,
            "incomeAccount": income_account_id,
            "outcomeAccount": "",
            "amount": amount,
            "extraData": extraData,
            "signature": signature,
            "status": "FAILED",
            "message": "Error occured in creating transaction!"
        }
        obj.wfile.write(dump_response(output_data))