from Task_management_system.app_config.tasks_queue import task_queue

class TaskManager:
    def __init__(self):
        self.task_statuses = {}

    async def process_tasks(self):
        while True:
            task = await task_queue.queue.get()
            await self.execute_task(task)

    async def execute_task(self, task):
        task_type = task.get("type")
        task_id = task.get("task_id")

        try:
            self.task_statuses[task_id] = {"status": "IN PROGRESS", "failure_reason": None}

            if task_type == "add_text":
                from Task_management_system.mongodb.mongo_utils import add_text_with_id
                await add_text_with_id(task["mongo_db"], task_id, task["text"])
            elif task_type == "add_file":
                from Task_management_system.mongodb.mongo_utils import add_file_with_id
                await add_file_with_id(task["mongo_db"], task_id, task["file_content"])

        except Exception as e:
            self.task_statuses[task_id] = {"status": "FAILED", "failure_reason": str(e)}
        else:
            self.task_statuses[task_id] = {"status": "DONE", "failure_reason": None}

task_manager = TaskManager()