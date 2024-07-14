import asyncio
from typing import Set
from httpx import AsyncClient


class RateLimitedClient(AsyncClient):
    # https://github.com/encode/httpx/issues/815#issuecomment-1625374321
    _bg_tasks: Set[asyncio.Task] = set()

    def __init__(self, interval: float = 1, count=1, **kwargs):
        self.interval = interval
        self.semaphore = asyncio.Semaphore(count)
        super().__init__(**kwargs)

    def _schedule_semaphore_release(self):
        wait = asyncio.create_task(asyncio.sleep(self.interval))
        RateLimitedClient._bg_tasks.add(wait)

        def wait_cb(task):
            self.semaphore.release()
            RateLimitedClient._bg_tasks.discard(task)

        wait.add_done_callback(wait_cb)

    async def send(self, *args, **kwargs):
        await self.semaphore.acquire()
        send = asyncio.create_task(super().send(*args, **kwargs))
        self._schedule_semaphore_release()
        return await send
