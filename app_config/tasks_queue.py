import asyncio
from Task_management_system.app_config.task_manager import task_manager

async def process_tasks():
    await task_manager.process_tasks()

loop = asyncio.get_event_loop()
loop.create_task(process_tasks())
