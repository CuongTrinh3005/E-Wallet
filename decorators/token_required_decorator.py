from functools import wraps

# class NonTokenError(Exception):
#     def __init__(self, value = "Token Required!!!"):
#         self.value = value
#     def __str__(self):
#         return repr(self.value)

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         authToken = args[0]
#         if not authToken:
#             raise NonTokenError()
#             # return {"message": "Unauthorized"}, 401
#         return f(*args, **kwargs)
#     return decorated