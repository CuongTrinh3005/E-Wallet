PORT = 8000
request_methods = {
    'GET_METHOD':[
        {
            'root': '/',
            'get_all_merchants': '/merchants',
            'account_token': '/account/token'
        }
    ],
    'POST_METHOD': [
        {
            'merchant_signup': '/merchant/signup',
            'create_account': '/account',
            'transaction_create': '/transaction/create',
            'transaction_confirm': '/transaction/confirm',
            'transaction_verify': '/transaction/verify',
            'transaction_cancel': '/transaction/cancel',
            'change_order_status': '/merchant/change-order-status'
        }
    ]
}