import pymongo
import uuid
from Task_management_system.mongodb.startup import DATABASE_NAME


async def validate_file(filename, filesize, get_config_field):
    file_extension = filename.split('.')[-1] if "." in filename else None
    valid_extension = file_extension in get_config_field("file_upload.extensions")
    valid_filesize = filesize <= get_config_field("file_upload.filesize_max")
    return valid_extension and valid_filesize, file_extension


async def add_text_task(task_id, text, config):
    try:
        print(f"Processing task {task_id}: Adding text to the database: {text}")

        # Генерируем уникальный идентификатор текста
        text_id = str(uuid.uuid4())

        users_collection = config.mongo[DATABASE_NAME]["users"]
        await users_collection.insert_one({"task_id": text_id, "text": text})

        print(f"Task {task_id}: Text added successfully with text_id: {text_id}")

        return text_id
    except Exception as e:
        print(f"Task {task_id}: Error adding text to the database: {str(e)}")
        raise