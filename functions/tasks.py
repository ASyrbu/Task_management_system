import pymongo
import uuid
from Task_management_system.mongodb.startup import DATABASE_NAME


async def validate_file(filename, filesize, get_config_field):
    file_extension = filename.split('.')[-1] if "." in filename else None
    valid_extension = file_extension in get_config_field("file_upload.extensions")
    valid_filesize = filesize <= get_config_field("file_upload.filesize_max")
    return valid_extension and valid_filesize, file_extension

