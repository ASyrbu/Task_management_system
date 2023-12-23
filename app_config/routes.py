from sanic import response
from Task_management_system.mongodb.startup import DATABASE_NAME
import uuid
from Task_management_system.authentification import functionality
from Task_management_system.mongodb.mongo_utils import add_text_with_id
import Task_management_system.mongodb.mongo_utils as mongo_db
import Task_management_system.redisdb.redis_utils as redis_db
import Task_management_system.utils.route_signature as routes_sign
from Task_management_system.utils.permissions_utils import check_user_permission
from Task_management_system.utils.raise_utils import json_response
from Task_management_system.utils.auth_hash import generate_user_id
from Task_management_system.utils.token_utils import generate_auth_user_pack, generate_registration_code
from Task_management_system.app_config.tasks_queue import task_manager


async def route_add_text(request):
    try:
        body = request.body

        if not body:
            return response.json({"error": "Empty text provided"}, status=400)

        text_add = body.decode('utf-8')

        task_id = str(uuid.uuid4())

        await add_text_with_id(request.app.ctx.mongo[DATABASE_NAME], task_id, text_add)

        return response.json({
            "task_id": task_id,
            "message": "Text added successfully",
            "added_text": text_add,
        })

    except Exception as err:
        return response.json({"error": str(err)}, status=500)

async def route_get_task_status(request, task_id):
    try:
        status_info = task_manager.task_statuses.get(task_id, {})

        if status_info:
            return response.json({
                "task_id": task_id,
                "status": status_info.get("status"),
                "failure_reason": status_info.get("failure_reason"),
            })
        else:
            task_manager.task_statuses[task_id] = {"status": "FAILED", "failure_reason": "This id does not exist in the database"}
            return response.json({
                "error": "Text not found",
                "status": "FAILED",
                "failure_reason": "This id does not exist in the database"
            }, status=404)

    except Exception as err:
        task_manager.task_statuses[task_id] = {"status": "FAILED", "failure_reason": str(err)}
        return response.json({"error": str(err)}, status=500)
async def find_text_by_id(request, task_id):
    try:
        result = await request.app.ctx.mongo[DATABASE_NAME]["users"].find_one({"task_id": task_id})

        if result:
            return response.json({
                "text_id": result.get("task_id"),
                "text": result.get("text"),
            })
        else:
            return response.json({"error": "Text not found"}, status=404)

    except Exception as err:
        return response.json({"error": str(err)}, status=500)

async def route_get_text(request, task_id):
    return await find_text_by_id(request, task_id)


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

