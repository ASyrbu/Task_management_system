urls = {
    "LOGIN": "/api/login",
    "REGISTRATION": "/api/registration",
    "REG_CODE_CHECK": "/api/registration/check_code",
    "REG_CODE_CREATE": "/api/admin/create_code"
}

registration_credentials = {
    "login": "gaam",
    "password": "gaam",
    "email": "gaam@gmail.com",
    "registration_code": "code_1234"
}

login_credential = {
    "login": "gaam",
    "password": "gaam"
}


def api_url(path):
    return f"http://127.0.0.1:4000{path}"
