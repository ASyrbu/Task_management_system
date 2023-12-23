from Task_management_system.app_config.task_manager import task_manager

async def process_tasks():
    await task_manager.process_tasks()

# Добавим задачу в экземпляр TaskManager
task_manager.add_task(process_tasks())
