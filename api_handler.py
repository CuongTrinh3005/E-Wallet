import json
import http.server
import socketserver
from typing import Tuple
from http import HTTPStatus
from config.api_config import request_methods
from config.db_config import connect
from services.account_services import generate_jwt, insert_account, insert_account_without_merchant
from services.merchant_services import insert_merchant
from enums.TypeEnum import TypeEnum
from utils.url_extractor import extract_account_id_in_url

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
    
    def do_GET(self):
        # get_requests_dict = request_methods['GET_METHOD'][0]
        # get_requests = list(get_requests_dict.values()) 
        # if self.path in get_requests:
        # if self.path == get_requests_dict['root']:
        if self.path == '/':
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {
                "status": "OK",
                "message": "Hello World! My name is Trinh Quoc Cuong"
            }
            self.wfile.write(dump_response(response))

        # elif self.path == get_requests_dict['get_all_merchants']:
        elif self.path == "/merchants":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {
                "status": "OK",
                "message": "Get all merchants"
            }
            self.wfile.write(dump_response(response))

        elif self.path.find('account') > -1 and self.path.find('token') > -1:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            account_id = extract_account_id_in_url(self.path)
            jwt_token_list = generate_jwt(account_id)
            # response = {
            #     # "token": jwt_token
            #     jwt_token
            # }
            self.wfile.write(bytes(jwt_token_list, 'utf-8'))


    def do_POST(self):
        post_requests_dict = request_methods['POST_METHOD'][0]
        post_requests = list(post_requests_dict.values()) 

        if self.path in post_requests:
            if self.path == post_requests_dict['merchant_signup']:
                # - request -
                input_data = self.get_data_sent()
                print(f'\nInput data: {input_data}\n')
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

                account_id = insert_account_without_merchant(connection, cursor, account_type, '', '')

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

            elif self.path == post_requests_dict['transaction_create']:
                input_data = self.get_data_sent()
                print(f'\nInput data: {input_data}\n')

                # - response -
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                
                output_data = {
                    "transactionId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "merchantId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "incomeAccount": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "outcomeAccount": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "amount": 0,
                    "extraData": "string",
                    "signature": "225744eba143248ae232bf81d6366b66",
                    "status": "INITIALIZED"
                }
                self.wfile.write(dump_response(output_data))

            elif self.path == post_requests_dict['transaction_confirm']:
                input_data = self.get_data_sent()
                print(f'\nInput data: {input_data}\n')

                # - response -
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                
                output_data = {
                    "code": "SUC",
                    "message": "string"
                }
                self.wfile.write(dump_response(output_data))

            elif self.path == post_requests_dict['transaction_verify']:
                input_data = self.get_data_sent()
                print(f'\nInput data: {input_data}\n')

                # - response -
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                
                # output_data = {
                #     "code": "SUC",
                #     "message": "string"
                # }
                # self.wfile.write(dump_response(output_data))

            elif self.path == post_requests_dict['transaction_cancel']:
                input_data = self.get_data_sent()
                print(f'\nInput data: {input_data}\n')

                # - response -
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                
                # output_data = {
                #     "code": "SUC",
                #     "message": "string"
                # }
                # self.wfile.write(dump_response(output_data))

    def get_data_sent(self):
        content_length = int(self.headers['Content-Length'])
        if content_length:
            input_json = self.rfile.read(content_length)
            input_data = json.loads(input_json)
        else:
            input_data = None

        return input_data

    # def send_response(self, res_data):
    #     self.send_response(200)
    #     self.send_header('Content-type', 'text/json')
    #     self.end_headers()

    #     self.wfile.write(dump_response(res_data))

    
            