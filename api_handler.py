import json
import http.server
import socketserver
from typing import Tuple
from http import HTTPStatus
from api_process import cancel_transaction, confirm_transaction, create_transaction, test, verify_transaction
from config.api_config import request_methods
from config.db_config import connect

from services.account_services import check_valid_acc_type, decode_jwt, decode_merchant_jwt, generate_jwt, insert_account, insert_account_without_merchant, topup
from services.merchant_services import insert_merchant
from enums.TypeEnum import TypeEnum
from services.transaction_services import create_signature, update_order_status
from utils.url_extractor import extract_account_id_in_url
from decorators.expired_decorator import TimeoutError

def dump_response(dict_data):
    output_json = json.dumps(dict_data)
    return output_json.encode('utf-8')

def get_connection_and_cursor():
    return connect()

def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)

    return obj

class APIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer):
        super().__init__(request, client_address, server)

    # request = self
    def get_request(self):
        return self
    
    def do_GET(self):
        get_requests_dict = request_methods['GET_METHOD'][0]
        if self.path == get_requests_dict['root']:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {
                "status": "OK",
                "message": "Hello World! My name is Trinh Quoc Cuong"
            }
            self.wfile.write(dump_response(response))

        elif self.path == get_requests_dict['get_all_merchants']:
            try:
                test(self)
            except TimeoutError:
                print("In try-catch block!")

        elif self.path.find('account') > -1 and self.path.find('token') > -1:
            connection, cursor = get_connection_and_cursor()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            account_id = extract_account_id_in_url(self.path)
            jwt_token = generate_jwt(account_id, connection, cursor)
 
            # self.wfile.write(bytes(jwt_token, 'utf-8'))
            self.wfile.write((json.dumps(jwt_token).encode('utf-8')))


    def do_POST(self):
        post_requests_dict = request_methods['POST_METHOD'][0]

        # if self.path in post_requests:
        if self.path == post_requests_dict['merchant_signup']:
            # - request -
            input_data = self.get_data_sent()
            connection, cursor = get_connection_and_cursor()
            merchant_id, api_key = insert_merchant(connection, cursor, input_data['merchantName'], input_data['merchantUrl'])
            account_id = insert_account(connection, cursor, TypeEnum.Merchant.value, '', merchant_id)

            # - response -
            self.send_response(200)
            self.send_header('Content-type', 'text/json')
            self.end_headers()
            
            output_data = {
                "merchantName": input_data['merchantName'],
                "accountId": account_id,
                "merchantId": merchant_id,
                "apiKey": api_key,
                "merchantUrl": input_data['merchantUrl']
            }
            self.wfile.write(dump_response(output_data))
            # self.send_response(output_data)

        elif self.path == post_requests_dict['create_account']:
            connection, cursor = get_connection_and_cursor()
            input_data = self.get_data_sent()
            print(f'\nInput data: {input_data}\n')
            account_type = ''
            if input_data['accountType'].lower() == TypeEnum.Personal.value:
                account_type = TypeEnum.Personal.value
            elif input_data['accountType'].lower() == TypeEnum.Issuer.value:
                account_type = TypeEnum.Issuer.value

            account_id = insert_account_without_merchant(connection, cursor, account_type, '')

            # - response -
            self.send_response(200)
            self.send_header('Content-type', 'text/json')
            self.end_headers()
            
            output_data = {
                "accountType": account_type,
                "accountId": account_id,
                "balance": 0
            }
            self.wfile.write(dump_response(output_data))

        elif self.path.find('account') > -1 and self.path.find('topup') > -1:
            jwt_token = self.headers['Authorization']
            if not jwt_token:
                self.send_response(401)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
            else:
                account_id = decode_jwt(jwt_token)
                output_data = {}
                connection, cursor = get_connection_and_cursor()
                is_valid = check_valid_acc_type(connection, cursor, account_id)
                if is_valid == 1:
                    output_data['valid_account_sender'] = True
                else: 
                    output_data['valid_account_sender'] = False

                input_data = self.get_data_sent()
                receiver_account_id = input_data['accountId']
                amount = float(input_data['amount'])

                # is_personal_account = check_valid_acc_type(connection, cursor, uuid.UUID(receiver_account_id).hex, TypeEnum.Personal.value)
                is_personal_account = check_valid_acc_type(connection, cursor, receiver_account_id, TypeEnum.Personal.value)
                if amount <= 0 or is_personal_account == 0:
                    output_data['message'] = 'Receiver must be personal account and amount must be larger than 0'
                    self.send_response(400)
                    self.send_header('Content-type', 'text/json')
                    self.end_headers()
                    self.wfile.write(dump_response(output_data))
                else:
                    topup(connection, cursor, receiver_account_id, amount)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/json')
                    self.end_headers()

        elif self.path == post_requests_dict['transaction_create']:
            input_data = self.get_data_sent()
            connection, cursor = get_connection_and_cursor()

            merchant_id = input_data['merchantId']
            amount = input_data['amount']
            extraData = input_data['extraData']
            signature = create_signature(merchant_id, amount, extraData)

            create_transaction(self, connection, cursor, merchant_id, amount, extraData, signature)

        elif self.path == post_requests_dict['transaction_confirm']:
            connection, cursor = get_connection_and_cursor()
            input_data = self.get_data_sent()

            transaction_id = input_data['transactionId']

            confirm_transaction(self, connection, cursor, transaction_id)

        elif self.path == post_requests_dict['transaction_verify']:
            connection, cursor = get_connection_and_cursor()
            input_data = self.get_data_sent()

            transaction_id = input_data['transactionId']
            verify_transaction(self, connection, cursor, transaction_id)

        elif self.path == post_requests_dict['transaction_cancel']:
            connection, cursor = get_connection_and_cursor()
            input_data = self.get_data_sent()

            transaction_id = input_data['transactionId']
            cancel_transaction(self, connection, cursor, transaction_id)

        elif self.path == post_requests_dict['change_order_status']:
            input_data = self.get_data_sent()
            self.send_response(200)
            self.send_header('Content-type', 'text/json')
            self.end_headers()
            
            output_data = {
                "order_id": input_data['order_id'],
                "status": input_data['status']
            }
            update_order_status(data=output_data)
            self.wfile.write(dump_response(output_data))

        elif self.path == '/decode/merchant':
            connection, cursor = get_connection_and_cursor()
            input_data = self.get_data_sent()
            token = input_data['token']
            merchant_id = input_data['merchant_id']

            merchant_account_id = decode_merchant_jwt(token, connection, cursor, merchant_id)

            self.send_response(200)
            self.send_header('Content-type', 'text/json')
            self.end_headers()

            output_data = {
                "merchant_account_id": merchant_account_id
            }
            
            self.wfile.write(dump_response(output_data))

        elif self.path == '/decode/notmerchant':
            input_data = self.get_data_sent()
            token = input_data['token']

            account_id = decode_jwt(token)

            self.send_response(200)
            self.send_header('Content-type', 'text/json')
            self.end_headers()

            output_data = {
                "account_id": account_id
            }
            
            self.wfile.write(dump_response(output_data))


    def get_data_sent(self):
        content_length = int(self.headers['Content-Length'])
        if content_length:
            input_json = self.rfile.read(content_length)
            input_data = json.loads(input_json)
        else:
            input_data = None

        return input_data