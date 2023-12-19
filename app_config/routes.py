from Task_management_system.app_config.task_manager import task_manager
from sanic import response
from Task_management_system.authentification import functionality
from Task_management_system.mongodb import mongo_utils
from Task_management_system.mongodb.mongo_utils import search_text_by_id
from Task_management_system.functions.tasks import add_text_task
import Task_management_system.mongodb.mongo_utils as mongo_db
import Task_management_system.redisdb.redis_utils as redis_db
import Task_management_system.utils.route_signature as routes_sign
from Task_management_system.utils.permissions_utils import check_user_permission
from Task_management_system.utils.raise_utils import json_response
from Task_management_system.utils.auth_hash import generate_user_id
from Task_management_system.utils.token_utils import generate_auth_user_pack, generate_registration_code


async def route_get_task_status(request):
    try:
        task_id = request.args.get("task_id")

        if not task_id:
            return response.json({"error": "Task ID is not provided"}, status=400)

        task_status, failure_reason = task_manager.get_task_status(task_id)

        return response.json({
            "task_id": task_id,
            "status": task_status,
            "failure_reason": failure_reason
        })
    except Exception as e:
        return response.json({"error": str(e)}, status=500)


async def route_add_text(request):
    try:
        body = request.body

        if not body:
            return response.json({"error": "Empty text provided"}, status=400)

        text_add = body.decode('utf-8')
        task_id = await task_manager.add_task(add_text_task, text_add, request.app.config)

        return response.json({
            "task_id": task_id,
            "message": "Text added successfully",
            "added_text": text_add,
        })

    except Exception as err:
        return response.json({"error": str(err)}, status=500)


async def add_response_headers(_, responses):
    responses.headers["Accept"] = "application/json"


async def login_route(request):
    user_data: dict = request.json

    if not functionality.validate_schema_login_route(user_data):
        return json_response(400, description=f"Provided fields are not Valid.")

    sanic_ref = request.route.ctx.refsanic.ctx

    user_id = generate_user_id(user_data)
    user_signature = {"id": user_id}

    user_exist = await mongo_db.exists_user(sanic_ref.mongo, user_signature)
    if not user_exist:
        return json_response(401, description=f'User was not found.')

    token, session_id = generate_auth_user_pack()
    await redis_db.remember_user_session(sanic_ref.redis, token, user_id, session_id)

    return json_response(200, token=token, session_id=session_id, user_id=user_id, description=f"Success.")


async def create_registration_code_route(request):
    user_data: dict = request.json

    if not functionality.validate_schema_create_reg_code(user_data):
        return json_response(400, description=f"Provided fields are not Valid.")

    sanic_ref = request.route.ctx.refsanic.ctx

    is_good = await check_user_permission(routes_sign.CreateRegistrationCode(sanic_ref=sanic_ref,
                                                                             user_data=user_data))
    if not is_good:
        return json_response(401, description=f"You dont have access.")

    reg_code = generate_registration_code()

    await redis_db.insert_registration_code(sanic_ref.redis, reg_code, user_data.get("role"))

    new_token = await functionality.update_user_token(
        user_id=user_data["user_id"],
        session_id=user_data["session_id"],
        redis_db=sanic_ref.redis)

    return json_response(200, token=new_token, code=reg_code, description="Registered.")


async def check_registration_code_route(request):
    user_data: dict = request.json

    if not functionality.validate_schema_registration_code(user_data):
        return json_response(400, description=f"Provided fields are not Valid.")

    sanic_ref = request.route.ctx.refsanic.ctx

    if not await redis_db.find_registration_code(sanic_ref.redis, user_data.get("register_code")):
        return json_response(401, description=f"Not valid code.")

    return json_response(200, description=f"Valid Code.")


async def register_route(request):
    user_data: dict = request.json

    if not functionality.validate_schema_registration_route(user_data):
        return json_response(400, description=f"Provided fields are not valid.")

    sanic_ref = request.route.ctx.refsanic.ctx
    user_id, user_data = generate_user_id(user_data, get_user=True)

    user_role = await check_user_permission(
        routes_sign.RegisterAccount(sanic_ref=sanic_ref, user_data=user_data)
    )

    if not user_role:
        return json_response(401, description=f"You are not granted, to do so.")

    user_signature = {
        "email": user_data.get("email"),
        "login": user_data.get("login")
    }

    user_exist = await mongo_db.exists_user(sanic_ref.mongo, user_signature)
    if user_exist:
        return json_response(401, description=f"Email address or login is being used by another user.")

    user_data["role"] = user_role

    await mongo_db.register_user(sanic_ref.mongo, user_data)
    await redis_db.remove_registration_code(sanic_ref.redis, user_data.get("registration_code"))

    return json_response(200, description=f"Registered successfully.")


async def patch_user_route(request):
    user_data: dict = request.json

    if not functionality.validate_schema_patch_user(user_data):
        return json_response(400, description=f"Provided fields are not valid.")

    sanic_ref = request.route.ctx.refsanic.ctx

    can_user_change_settings = await check_user_permission(
        routes_sign.SettingsAccount(sanic_ref=sanic_ref, user_data=user_data)
    )

    if not can_user_change_settings:
        return json_response(401, description=f"You are not valid.")

    await mongo_db.replace_settings(mongo_db, user_data["user_id"], user_data["settings"])

    new_token = await functionality.update_user_token(
        user_id=user_data["user_id"],
        session_id=user_data["session_id"],
        redis_db=sanic_ref.redis)

    return json_response(200, token=new_token, description=f"Success.")

async def route_search_text_by_id(request):
    try:
        task_id = request.json.get("task_id")

        if not task_id:
            return response.json({"error": "Task ID is not provided"}, status=400)

        mongo_db = request.app.ctx.mongo

        # Поиск текста по ID
        text = await mongo_utils.search_text_by_id(mongo_db, task_id)

        if not text:
            return response.json({"error": "Text not found"}, status=404)

        return response.json({"text": text})

    except Exception as e:
        print("Error in route_search_text_by_id:", str(e))
        return response.json({"error": str(e)}, status=500)


