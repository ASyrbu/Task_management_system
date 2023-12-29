import asyncio

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

    async def add_task_to_queue(self, task, task_id, args, kwargs):
        await self.task_queue.put((task, task_id, args, kwargs))


task_manager = TaskManager()
