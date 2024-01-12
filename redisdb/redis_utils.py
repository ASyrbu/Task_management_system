from Task_management_system.app_config.task_manager import task_manager

async def remember_user_session(redis_db, token, user_id, session_id, expire_in_seconds=900):
    await redis_db.setex(user_id, expire_in_seconds, f"{session_id},{token}")


async def find_registration_code(redis_db, reg_code):
    response = await redis_db.get(reg_code)
    return response


async def remove_registration_code(redis_db, reg_code):
    await redis_db.delete(reg_code)


async def insert_registration_code(redis_db, reg_code: str, user_type: str, expire_in_seconds=900) -> None:
    await redis_db.setex(reg_code, expire_in_seconds, user_type)


async def check_user_token(redis_db, user_id, session_id, token):
    response = await redis_db.get(user_id)
    return session_id in response and token in response


async def add_text_with_id(redis_db, text_id, text) -> None:
    try:
        print(f"Adding text with id {text_id}: {text}")
        await redis_db.hset("text_collection", text_id, text)
        print(f"Text with id {text_id} added successfully")
    except Exception as e:
        print(f"Error adding text with id {text_id}: {str(e)}")
        task_manager.task_statuses[text_id] = {"status": "FAILED", "failure_reason": str(e)}
        raise
    else:
        task_manager.task_statuses[text_id] = {"status": "DONE", "failure_reason": None}

async def add_file_with_id(redis_db, file_id, file_content):
    try:
        print(f"Adding file with id {file_id}")
        await redis_db.set(file_id, file_content)
        print(f"File with id {file_id} added successfully")
    except Exception as e:
        print(f"Error adding file with id {file_id}: {str(e)}")
        task_manager.task_statuses[file_id] = {"status": "FAILED", "failure_reason": str(e)}
        raise
    else:
        task_manager.task_statuses[file_id] = {"status": "DONE", "failure_reason": None}

async def delete_text_by_id(redis_db, text_id):
    try:
        print(f"Deleting text with id {text_id}")
        await redis_db.hdel("text_collection", text_id)
        print(f"Text with id {text_id} deleted successfully")
    except Exception as e:
        print(f"Error deleting text with id {text_id}: {str(e)}")
        raise