import json
import http.server
import socketserver
from typing import Tuple
from http import HTTPStatus
from config.api_config import request_methods

def dump_response(dict_data):
    output_json = json.dumps(dict_data)
    return output_json.encode('utf-8')

class APIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer):
        super().__init__(request, client_address, server)

    # @property
    # def api_response(self, data):
    #     return json.dumps(data).encode()

    def do_GET(self):
        get_requests_dict = request_methods['GET_METHOD'][0]
        get_requests = list(get_requests_dict.values()) 
        if self.path in get_requests:
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
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json")
                self.end_headers()

                response = {
                    "status": "OK",
                    "message": "Get all merchants"
                }
                self.wfile.write(dump_response(response))


    def do_POST(self):
        post_requests_dict = request_methods['POST_METHOD'][0]
        post_requests = list(post_requests_dict.values()) 
        if self.path in post_requests:
            if self.path == post_requests_dict['merchant_signup']:
                # - request -
                input_data = self.get_data_sent()
                print(f'\nInput data: {input_data}\n')

                # - response -
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                
                output_data = {
                    "merchantName": "1e7f588e-ad4e-436e-b8f5-4a0dd3416b19",
                    "accountId": "e5cc7ef9-8da1-4ca9-9df5-46cc08c98760",
                    "merchantId": "dd6de58e-fc7b-4138-bb4a-bd70be05689a",
                    "apiKey": "bdd6a784-0da5-45da-a83c-7bbe1d34db35",
                    "merchantUrl": "http://localhost:8080"
                }
                self.wfile.write(dump_response(output_data))
                # self.send_response(output_data)

            elif self.path == post_requests_dict['create_account']:
                input_data = self.get_data_sent()
                print(f'\nInput data: {input_data}\n')

                # - response -
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                
                output_data = {
                    "accountType": "personal",
                    "accountId": "2fa606d2-9b42-41fc-9622-5f5ab2081082",
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

    
            