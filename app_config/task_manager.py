import asyncio
import uuid
from Task_management_system.mongodb.mongo_utils import add_text_with_id, add_file_with_id, delete_text_by_id

class TaskManager:
    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.task_statuses = {}

    async def process_tasks(self):
        while True:
            task, task_id, args, kwargs = await self.task_queue.get()
            try:
                self.task_statuses[task_id] = {"status": "IN PROGRESS", "failure_reason": None}
                await task(*args, **kwargs)
                self.task_statuses[task_id] = {"status": "DONE", "failure_reason": None}
            except Exception as e:
                self.task_statuses[task_id] = {"status": "FAILED", "failure_reason": str(e)}
                print(f"Error processing task {task_id}: {e}")
            finally:
                self.task_queue.task_done()

task_manager = TaskManager()
