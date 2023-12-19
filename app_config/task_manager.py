import asyncio

class TaskManager:
    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.task_statuses = {}  # Словарь для хранения статусов задач

    async def process_tasks(self):
        while True:
            task = await self.task_queue.get()
            task_id = task.__name__
            try:
                await task()
                self.task_statuses[task_id] = {"status": "DONE", "failure_reason": None}
            except Exception as e:
                self.task_statuses[task_id] = {"status": "FAILED", "failure_reason": str(e)}
                print(f"Error processing task: {e}")
            finally:
                self.task_queue.task_done()

    async def add_task(self, task):
        task_id = task.__name__
        self.task_statuses[task_id] = {"status": "PENDING", "failure_reason": None}
        await self.task_queue.put(task)

    def get_task_status(self, task_id):
        status_info = self.task_statuses.get(task_id, {"status": "UNKNOWN", "failure_reason": None})
        return status_info["status"], status_info["failure_reason"]

task_manager = TaskManager()
