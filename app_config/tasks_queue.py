import asyncio
from Task_management_system.app_config.task_manager import task_manager
from Task_management_system.mongodb.mongo_utils import add_text_with_id, add_file_with_id
async def process_tasks():
    await task_manager.process_tasks()

loop = asyncio.get_event_loop()
loop.create_task(process_tasks())

async def enqueue_add_text_task(task_id, text_add, mongo_db):
    await task_manager.add_task_to_queue(add_text_with_id, task_id, [mongo_db, task_id, text_add], {})

async def enqueue_add_file_task(file_id, file_content, mongo_db):
    await task_manager.add_task_to_queue(add_file_with_id, file_id, [mongo_db, file_id, file_content], {})
