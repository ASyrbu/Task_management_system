from functools import singledispatch
from Task_management_system.mongodb import mongo_utils as mongo_query
from Task_management_system.redisdb import redis_utils as redis_query
from Task_management_system.utils import route_signature as signatures
from rapidjson import loads


async def is_user_actually_logged(sanic_ref, user_data):
    if not await redis_query.check_user_token(sanic_ref.redis,
                                              user_data.get("user_id"),
                                              user_data.get("session_id"),
                                              user_data.get("token")):
        return False
    return True


@singledispatch
async def check_user_permission(_signature):
    raise NotImplementedError(_signature)


@check_user_permission.register(signatures.CreateRegistrationCode)
async def _(signature_data) -> bool:
    logged_in = await is_user_actually_logged(signature_data["sanic_ref"], signature_data["user_data"])
    if not logged_in:
        return False

    mongo_db = signature_data["sanic_ref"].mongo
    get_users_data = signature_data["user_data"].get

    requested_permissions = {
        "id": get_users_data("user_id"),
        "role": "admin"
    }

    return await mongo_query.check_permissions(mongo_db, requested_permissions)


@check_user_permission.register(signatures.RegisterAccount)
async def _(signature_data):
    redis_db = signature_data["sanic_ref"].redis
    get_users_data = signature_data["user_data"].get

    redis_reg_code = await redis_query.find_registration_code(redis_db, get_users_data("registration_code"))

    return loads(redis_reg_code)["role"] if isinstance(redis_reg_code, str) else False


@check_user_permission.register(signatures.SettingsAccount)
async def _(signature_data):
    logged_in = await is_user_actually_logged(signature_data["sanic_ref"], signature_data["user_data"])
    if not logged_in:
        return False
    return True
