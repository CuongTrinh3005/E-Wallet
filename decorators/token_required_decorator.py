from functools import wraps
# from api_handler import APIHandler

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         api_handler = APIHandler()
#         # data, status = Auth.get_logged_in_user(request)
#         request = api_handler.get_request()
#         token = request.headers['Authorization']

#         if not token:
#             request.send_response(401)
#             request.send_header('Content-type', 'text/json')
#             request.end_headers()

#         return f(*args, **kwargs)

#     return decorated