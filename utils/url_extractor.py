def extract_account_id_in_url(url):
    # '/account/ufidifodfidoioc/token' returns 'ufidifodfidoioc'
    account_id = url.split('/account/')[1].split('/')[0]
    if account_id != '':
        return account_id
    return ''