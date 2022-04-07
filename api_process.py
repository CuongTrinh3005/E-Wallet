import json
from http import HTTPStatus
import time

from decorators.expired_decorator import timeout

from enums.StatusEnum import StatusEnum
from enums.TypeEnum import TypeEnum
from services.account_services import check_valid_acc_type, decode_jwt, get_balance_of_account, transfer
from services.transaction_services import check_transaction_exist, confirm_transaction_service, get_amount_of_transaction, get_amount_of_transaction_for_transfering, get_extra_data, get_income_account_id, get_transaction_status, insert_new_transaction, update_order_status, update_transaction_status
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

    # sleep_print()
    response = {
        "status": "OK",
        "message": "Get all merchants"
    }
    obj.wfile.write(dump_response(response))

@timeout(5)
def create_transaction(obj, connection, cursor, merchant_id, amount, extraData, signature):
    try:
        jwt_token = obj.headers['Authorization']
        if not jwt_token:
            obj.send_response(401)
            obj.send_header('Content-type', 'text/json')
            obj.end_headers()
        else:
            income_account_id = decode_jwt(jwt_token)
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

            data = {
                "order_id": extraData,
                "status": StatusEnum.Expired.value
            }
            update_order_status(data=data)
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
        data = {
                "order_id": extraData,
                "status": StatusEnum.Failed.value
            }
        update_order_status(data=data)

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
            "message": "Error occured in creating transaction!",
            "message_error": str(ex)
        }
        obj.wfile.write(dump_response(output_data))

@timeout(5)
def confirm_transaction(obj, connection, cursor, transaction_id):
    try:
        jwt_token = obj.headers['Authorization']
        if not jwt_token:
            obj.send_response(401)
            obj.send_header('Content-type', 'text/json')
            obj.end_headers()
        else:
            personal_account_id = decode_jwt(jwt_token)
            # Assume error in creating process
            # x = 2/0

            # Assume error timeout in creating process
            # sleep_print()

            output_data = {}
            is_existed = check_transaction_exist(connection, cursor, transaction_id)
            if is_existed == 1:
                is_personal_account = check_valid_acc_type(connection, cursor, personal_account_id, TypeEnum.Personal.value)
                extraData = get_extra_data(connection, cursor, transaction_id)
                if is_personal_account == 1:
                    transaction_amount = get_amount_of_transaction(connection, cursor, transaction_id)
                    personal_account_balance = get_balance_of_account(connection, cursor, account_id=personal_account_id)
                    if personal_account_balance >= transaction_amount:
                        # Personal has enough balance to confirm transaction
                        confirm_transaction_service(connection, cursor, transaction_id, personal_account_id)
                        data = {
                            "order_id": extraData,
                            "status": StatusEnum.Confirmed.value
                        }
                        update_order_status(data=data)
                        # - response -
                        obj.send_response(200)
                        obj.send_header('Content-type', 'text/json')
                        obj.end_headers()
                        
                        output_data['code'] = "SUC"
                        output_data['message'] = f"Transaction with id = {transaction_id} have been confirmed!"
                    else:
                        # is_existed = check_transaction_exist(connection, cursor, transaction_id)
                        update_transaction_status(connection, cursor, transaction_id, StatusEnum.Failed.value)
                        extraData = get_extra_data(connection, cursor, transaction_id)
                        data = {
                            "order_id": extraData,
                            "status": StatusEnum.Failed.value
                        }
                        update_order_status(data=data)

                        obj.send_response(400)
                        obj.send_header('Content-type', 'text/json')
                        obj.end_headers()
                        
                        output_data['message'] = "Balance is not enough to confirm transaction!"
                else:
                    obj.send_response(400)
                    obj.send_header('Content-type', 'text/json')
                    obj.end_headers()
                    output_data = {"message": "You need have a personal account for confirming transaction!"}

                # obj.wfile.write(dump_response(output_data))
            else:
                obj.send_response(400)
                obj.send_header('Content-type', 'text/json')
                obj.end_headers()
                output_data = {"message": "Transaction is not existed!"}

            obj.wfile.write(dump_response(output_data))
    
    except TimeoutError:
        # If expired confirm transaction
        if transaction_id != '':
            update_transaction_status(connection, cursor, transaction_id, StatusEnum.Expired.value)
            extraData = get_extra_data(connection, cursor, transaction_id)
            data = {
                "order_id": extraData,
                "status": StatusEnum.Expired.value
            }
            update_order_status(data=data)
        obj.send_response(200)
        obj.send_header('Content-type', 'text/json')
        obj.end_headers()
        
        output_data = {
            "transactionId": transaction_id,
            "status": "EXPIRED",
            "message": "Transaction is exceed the limit time!"
        }
        obj.wfile.write(dump_response(output_data))
    except Exception as ex:
        print("Exception: ", ex)
        update_transaction_status(connection, cursor, transaction_id, StatusEnum.Failed.value)
        extraData = get_extra_data(connection, cursor, transaction_id)
        data = {
            "order_id": extraData,
            "status": StatusEnum.Failed.value
        }
        update_order_status(data=data)
        obj.send_response(200)
        obj.send_header('Content-type', 'text/json')
        obj.end_headers()
        
        output_data = {
            "transactionId": transaction_id,
            "message": "Error occured in confirming transaction! Try again!",
            "message_error": str(ex)
        }
        obj.wfile.write(dump_response(output_data))

@timeout(5)
def verify_transaction(obj, connection, cursor, transaction_id):
    try:
        jwt_token = obj.headers['Authorization']
        if not jwt_token:
            obj.send_response(401)
            obj.send_header('Content-type', 'text/json')
            obj.end_headers()
        else:
            personal_account_id = decode_jwt(jwt_token)

            # Assume error in creating process
            # x = 2/0

            # Assume error timeout in creating process
            sleep_print()

            output_data = {}
            is_existed = check_transaction_exist(connection, cursor, transaction_id)
            send_message = True
            if is_existed == 1:
                extraData = get_extra_data(connection, cursor, transaction_id)
                merchant_account_id = get_income_account_id(connection, cursor, transaction_id)
                is_personal_account = check_valid_acc_type(connection, cursor, personal_account_id, TypeEnum.Personal.value)
                if is_personal_account == 1:
                    transaction_amount = get_amount_of_transaction_for_transfering(connection, cursor, transaction_id)
                    personal_account_balance = get_balance_of_account(connection, cursor, account_id=personal_account_id)
                    if personal_account_balance >= transaction_amount:
                        # Personal has enough balance to confirm transaction
                        transfer(connection, cursor, transaction_id, merchant_account_id, personal_account_id, transaction_amount)
                        update_transaction_status(connection, cursor, transaction_id, StatusEnum.Completed.value)
                        data = {
                            "order_id": extraData,
                            "status": StatusEnum.Completed.value
                        }
                        update_order_status(data=data)
                        # - response -
                        obj.send_response(200)
                        obj.send_header('Content-type', 'text/json')
                        obj.end_headers()
                        send_message = False
                    else:
                        update_transaction_status(connection, cursor, transaction_id, StatusEnum.Failed.value)
                        data = {
                            "order_id": extraData,
                            "status": StatusEnum.Failed.value
                        }
                        update_order_status(data=data)

                        obj.send_response(400)
                        obj.send_header('Content-type', 'text/json')
                        obj.end_headers()
                        
                        output_data['message'] = "Balance is not enough to verify transaction!"
                else:
                    obj.send_response(400)
                    obj.send_header('Content-type', 'text/json')
                    obj.end_headers()
                    output_data = {"message": "You need have a personal account for verifying transaction!"}
            else:
                obj.send_response(400)
                obj.send_header('Content-type', 'text/json')
                obj.end_headers()
                output_data = {"message": "Transaction is not existed!"}
            if send_message:
                obj.wfile.write(dump_response(output_data))
    except TimeoutError:
        # If expired confirm transaction
        if transaction_id != '':
            update_transaction_status(connection, cursor, transaction_id, StatusEnum.Expired.value)
            extraData = get_extra_data(connection, cursor, transaction_id)
            data = {
                "order_id": extraData,
                "status": StatusEnum.Expired.value
            }
            update_order_status(data=data)
        obj.send_response(200)
        obj.send_header('Content-type', 'text/json')
        obj.end_headers()
        
        output_data = {
            "transactionId": transaction_id,
            "status": "EXPIRED",
            "message": "Transaction is exceed the limit time!"
        }
        obj.wfile.write(dump_response(output_data))
    except Exception as ex:
        print("Exception: ", ex)
        update_transaction_status(connection, cursor, transaction_id, StatusEnum.Failed.value)
        extraData = get_extra_data(connection, cursor, transaction_id)
        data = {
            "order_id": extraData,
            "status": StatusEnum.Failed.value
        }
        update_order_status(data=data)
        obj.send_response(200)
        obj.send_header('Content-type', 'text/json')
        obj.end_headers()
        
        output_data = {
            "transactionId": transaction_id,
            "message": "Error occured in verifying transaction! Try again!",
            "message_error": str(ex)
        }
        obj.wfile.write(dump_response(output_data))

def cancel_transaction(obj, connection, cursor, transaction_id):
    extraData = ''
    jwt_token = obj.headers['Authorization']
    if not jwt_token:
            obj.send_response(401)
            obj.send_header('Content-type', 'text/json')
            obj.end_headers()
    else:
        personal_account_id = decode_jwt(jwt_token)

        is_existed = check_transaction_exist(connection, cursor, transaction_id)
        if is_existed == 1:
            extraData = get_extra_data(connection, cursor, transaction_id)
            is_personal_account = check_valid_acc_type(connection, cursor, personal_account_id, TypeEnum.Personal.value)
            if is_personal_account == 1:
                status = get_transaction_status(connection, cursor, transaction_id)
                if status != StatusEnum.Confirmed.value:
                    obj.send_response(400)
                    obj.send_header('Content-type', 'text/json')
                    obj.end_headers()
                    output_data = {"message": "Transaction must be confirmed before being canceled!"}
                    obj.wfile.write(dump_response(output_data))
                else:
                    obj.send_response(200)
                    obj.send_header('Content-type', 'text/json')
                    obj.end_headers()
                    update_transaction_status(connection, cursor, transaction_id, StatusEnum.Canceled.value)
                    data = {
                        "order_id": extraData,
                        "status": StatusEnum.Canceled.value
                    }
                    update_order_status(data=data)
            else:
                obj.send_response(400)
                obj.send_header('Content-type', 'text/json')
                obj.end_headers()
                output_data = {"message": "You need have a personal account for canceling transaction!"}
                obj.wfile.write(dump_response(output_data))
        else:
            obj.send_response(400)
            obj.send_header('Content-type', 'text/json')
            obj.end_headers()
            output_data = {"message": "Transaction is not existed!"}
            obj.wfile.write(dump_response(output_data))