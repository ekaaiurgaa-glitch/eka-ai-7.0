"""Message queue for async jobs."""
from typing import Dict, Callable
import asyncio
from datetime import datetime


class MessageQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.handlers: Dict[str, Callable] = {}
    
    def register_handler(self, task_type: str, handler: Callable):
        self.handlers[task_type] = handler
    
    async def enqueue(self, task_type: str, payload: Dict):
        await self.queue.put({"type": task_type, "payload": payload, "timestamp": datetime.utcnow()})
    
    async def process(self):
        while True:
            task = await self.queue.get()
            handler = self.handlers.get(task["type"])
            if handler:
                try:
                    await handler(task["payload"])
                except Exception as e:
                    print(f"Task failed: {e}")
            self.queue.task_done()


mq = MessageQueue()
