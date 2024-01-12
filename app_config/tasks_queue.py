from asyncio import Queue

class TaskQueue:
    def __init__(self):
        self.queue = Queue()

    async def enqueue_add_text_task(self, task_id, text, redis_db):
        await self.queue.put({"type": "add_text", "task_id": task_id, "text": text, "redis_db": redis_db})

    async def enqueue_add_file_task(self, file_id, file_content, redis_db):
        await self.queue.put({"type": "add_file", "file_id": file_id, "file_content": file_content, "redis_db": redis_db})


task_queue = TaskQueue()
