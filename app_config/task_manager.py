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
                await task()
                self.task_statuses[task_id] = {"status": "DONE", "failure_reason": None}
            except Exception as e:
                self.task_statuses[task_id] = {"status": "FAILED", "failure_reason": str(e)}
                print(f"Error processing task: {e}")
            finally:
                self.task_queue.task_done()

    async def add_task(self, task, *args, **kwargs):
        task_id = str(uuid.uuid4())  # Генерируем уникальный идентификатор для задачи
        self.task_statuses[task_id] = {"status": "PENDING", "failure_reason": None}
        await self.task_queue.put((task, task_id))
        return task_id


task_manager = TaskManager()