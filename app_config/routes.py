from sanic import response
from sanic import Unauthorized
from Task_management_system.mongodb.startup import DATABASE_NAME
import uuid
from Task_management_system.authentification import functionality
from Task_management_system.mongodb.mongo_utils import delete_text_by_id
import Task_management_system.mongodb.mongo_utils as mongo_db
import Task_management_system.redisdb.redis_utils as redis_db
import Task_management_system.utils.route_signature as routes_sign
from Task_management_system.utils.permissions_utils import check_user_permission
from Task_management_system.utils.raise_utils import json_response
from Task_management_system.utils.auth_hash import generate_user_id
from Task_management_system.utils.token_utils import generate_auth_user_pack, generate_registration_code
from Task_management_system.app_config.tasks_queue import task_queue
from Task_management_system.app_config.task_manager import task_manager


async def add_text(request):
    try:
        user_data = await get_user_data(request)

        if user_data is None:
            return response.json({"error": "User not authenticated"}, status=401)

        body = request.body

        if not body:
            return response.json({"error": "Empty text provided"}, status=400)

        text_add = body.decode('utf-8')

        task_id = str(uuid.uuid4())

        await task_queue.enqueue_add_text_task(task_id, text_add, request.app.ctx.mongo[DATABASE_NAME])

        return response.json({
            "task_id": task_id,
            "message": "Text add task enqueued successfully",
            "added_text": text_add,
        })

    except Unauthorized as err:
        return response.json({"error": str(err)}, status=401)
    except Exception as err:
        return response.json({"error": str(err)}, status=500)


async def add_file(request):
    try:
        user_data = await get_user_data(request)

        if user_data is None:
            raise Unauthorized("User not authenticated")

        file_field = request.files.get('file')

        if file_field is None:
            print("No file provided")
            return response.json({"error": "No file provided"}, status=400)

        file_content = file_field.body
        file_id = str(uuid.uuid4())

        # Use the task queue to add a file
        await task_queue.enqueue_add_file_task(file_id, file_content, request.app.ctx.mongo[DATABASE_NAME])

        return response.json({
            "task_id": file_id,
            "message": "File add task enqueued successfully",
        })

    except Unauthorized as err:
        return response.json({"error": str(err)}, status=401)
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return response.json({"error": str(e)}, status=500)

async def get_task_status(request, task_id):
    try:
        user_data = await get_user_data(request)

        if user_data is None:
            return response.json({"error": "User not authenticated"}, status=401)

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

    except Unauthorized as err:
        return response.json({"error": str(err)}, status=401)

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return response.json({"error": str(e)}, status=500)


async def find_text_by_id(request, task_id):
    try:
        user_data = await get_user_data(request)

        if user_data is None:
            return response.json({"error": "User not authenticated"}, status=401)
        result = await request.app.ctx.mongo[DATABASE_NAME]["users"].find_one({"task_id": task_id})

        if result:
            return response.json({
                "text_id": result.get("task_id"),
                "text": result.get("text"),
            })
        else:
            return response.json({"error": "Text not found"}, status=404)

    except Unauthorized as err:
        return response.json({"error": str(err)}, status=401)
    except Exception as e:
        return response.json({"error": str(e)}, status=500)


async def delete_text(request, text_id):
    try:
        user_data = await get_user_data(request)

        if user_data is None:
            return response.json({"error": "User not authenticated"}, status=401)

        await delete_text_by_id(request.app.ctx.mongo[DATABASE_NAME], text_id)

        return response.json({
            "message": f"Text with id {text_id} deleted successfully",
        })

    except Unauthorized as err:
        return response.json({"error": str(err)}, status=401)
    except Exception as err:
        return response.json({"error": str(err)}, status=500)


async def route_add_text(request):
    return await add_text(request)


async def route_delete_text(request, text_id):
    return await delete_text(request, text_id)


async def add_file_route(request):
    return await add_file(request)


async def route_get_text(request, task_id):
    return await find_text_by_id(request, task_id)


async def route_get_task_status(request, task_id):
    return await get_task_status(request, task_id)


async def add_response_headers(_, responses):
    responses.headers["Accept"] = "application/json"


async def get_user_data(request):
    user_id = request.headers.get('user_id')
    session_id = request.headers.get('session_id')
    token = request.headers.get('token')
    if user_id is None or session_id is None or token is None:
        raise Unauthorized("User Not Authorized")
    user_data = await redis_db.check_user_token(request.app.ctx.redis, user_id, session_id, token)
    return user_data


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
