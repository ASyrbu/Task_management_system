from Task_management_system.app_config.task_manager import TaskManager

task_manager = TaskManager()

async def process_tasks():
    await task_manager.process_tasks()