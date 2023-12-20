import asyncio
import uuid

class TaskManager:
    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.task_statuses = {}

    async def process_tasks(self):
        while True:
            task, task_id = await self.task_queue.get()
            try:
                self.task_statuses[task_id] = {"status": "PARSING", "failure_reason": None}
                await task()
                self.task_statuses[task_id] = {"status": "DONE", "failure_reason": None}
            except Exception as e:
                self.task_statuses[task_id] = {"status": "FAILED", "failure_reason": str(e)}
                print(f"Error processing task {task_id}: {e}")
            finally:
                self.task_queue.task_done()

    async def add_task(self, task, *args, **kwargs):
        task_id = str(uuid.uuid4())
        self.task_statuses[task_id] = {"status": "PENDING", "failure_reason": None}
        await self.task_queue.put((task, task_id))
        return task_id

    async def get_task_status(self, task_id):
        # Подождем некоторое время, чтобы задача точно успела обработаться
        await asyncio.sleep(1)
        status_info = self.task_statuses.get(task_id, {"status": "UNKNOWN", "failure_reason": None})
        return status_info["status"], status_info["failure_reason"]

    def get_all_task_ids(self):
        return list(self.task_statuses.keys())

task_manager = TaskManager()