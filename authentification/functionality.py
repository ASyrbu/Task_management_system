from Task_management_system.utils.token_utils import generate_auth_user_token


def validate_schema_login_route(schema) -> bool:
    field_login = schema.get("login")
    field_password = schema.get("password")
    if schema.__len__() != 2 \
            or not isinstance(field_login, str) \
            or not isinstance(field_password, str):
        return False
    return True


def validate_schema_registration_route(schema) -> bool:
    field_login = schema.get("login")
    field_password = schema.get("password")
    field_email = schema.get("email")
    field_reg_code = schema.get("registration_code")
    if schema.__len__() != 4 \
            or not isinstance(field_login, str) \
            or not isinstance(field_password, str) \
            or not isinstance(field_email, str) \
            or not isinstance(field_reg_code, str):
        return False
    return True


def validate_schema_create_reg_code(schema) -> bool:
    field_userid = schema.get("user_id")
    field_session = schema.get("session_id")
    field_token = schema.get("token")
    field_type = schema.get("role")

    if schema.__len__() != 4 \
            or not isinstance(field_userid, str) \
            or not isinstance(field_session, str) \
            or not isinstance(field_token, str) \
            or not isinstance(field_type, str):
        return False
    return True


def validate_schema_registration_code(schema) -> bool:
    field_code = schema.get("register_code")
    if schema.__len__() != 1 \
            or not isinstance(field_code, str):
        return False
    return True


def validate_schema_patch_user(schema) -> bool:
    field_user_id = schema.get("user_id")
    field_token = schema.get("token")
    field_session = schema.get("session_id")
    field_settings = schema.get("settings")

    if schema.__len__() != 4 \
            or not isinstance(field_settings, dict) \
            or not isinstance(field_user_id, str) \
            or not isinstance(field_token, str) \
            or not isinstance(field_session, str):
        return False
    return True


def compose_permission_request(user_data: dict, app_or_prod_id=None, system=False, user_settings=False):
    return {
        "target": app_or_prod_id,
        "user_settings": user_settings,
        "system": system,
        "user_id": user_data.get("user_id")
    }


async def update_user_token(user_id, session_id, redis_db):
    new_token = generate_auth_user_token()
    await redis_db.set(user_id, f"{session_id},{new_token}")
    return new_token
