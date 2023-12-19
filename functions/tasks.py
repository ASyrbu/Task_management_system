import pymongo
import uuid


async def validate_file(filename, filesize, get_config_field):
    file_extension = filename.split('.')[-1] if "." in filename else None
    valid_extension = file_extension in get_config_field("file_upload.extensions")
    valid_filesize = filesize <= get_config_field("file_upload.filesize_max")
    return valid_extension and valid_filesize, file_extension


async def add_text_task(user_id, text, config):
    try:
        mongo_uri = config["MONGO_URL"]
        database_name = config["DATABASE_NAME"]

        client = pymongo.MongoClient(mongo_uri)
        db = client[database_name]

        texts_collection = db["texts"]

        # Генерация уникального идентификатора для задачи
        task_id = str(uuid.uuid4())

        # Сохранение текста с уникальным идентификатором задачи
        result = texts_collection.insert_one({"task_id": task_id, "user_id": user_id, "text": text})

        client.close()

        return {"status": "success", "task_id": task_id, "message": "Text added successfully", "added_text": text}
    except Exception as e:
        print("Error in add_text_task:", str(e))
        return {"status": "error", "message": str(e)}
