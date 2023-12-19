from Task_management_system.mongodb.startup import DATABASE_NAME


async def exists_user(mongo_db, search) -> bool:
    result = await mongo_db["users"].find_one(search, {"id": 1})
    return result is not None


async def insert_registration_code(mongo_db, reg_code, permissions):
    await mongo_db["register_codes"].insert_one({
        "code": reg_code,
        "permissions": permissions
    })


async def find_registration_code(mongo_db, reg_code):
    response = await mongo_db["register_codes"].find_one({"code": reg_code}, {"_id": 0, "code": 1})
    return response


async def replace_settings(mongo_db, user_id, new_settings):
    await mongo_db["users"].replace_one({"id": user_id}, {"$set": new_settings})


async def check_permissions(mongo_db, requested_permissions: dict):
    permission = await mongo_db["users"].find_one(requested_permissions, {"id": 1})
    return permission is not None


async def register_user(mongo_db, user_data) -> None:
    await mongo_db["users"].insert_one({
        "login": user_data.get("login"),
        "password": user_data.get("password"),
        "email": user_data.get("email"),
        "role": user_data.get("role"),
        "id": user_data.get("id"),
        "telegram": None,
        "logs_access": user_data.get("permissions")
    })


async def add_text(mongo_db, text):
    try:
        print(f"Adding text: {text}")
        texts_collection = mongo_db["texts"]
        await texts_collection.insert_one({"text": text})
        print("Text added successfully")
    except Exception as e:
        print(f"Error adding text: {str(e)}")
        raise

async def search_text_by_id(mongo_db, text_id):
    text_collection = mongo_db["texts"]
    text = await text_collection.find_one({"task_id": text_id})
    return text.get("text") if text else None
