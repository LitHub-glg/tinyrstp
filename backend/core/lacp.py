import asyncio
import time
from typing import List, Callable
from backend.core.link import Link, LinkState


class LACPDetector:
    def __init__(self, probe_interval: float = 0.01, timeout: float = 0.03):
        self.probe_interval = probe_interval
        self.timeout = timeout
        self.links: List[Link] = []
        self.running = False
        self.on_failure: List[Callable[[Link], None]] = []
        self.on_recovery: List[Callable[[Link], None]] = []
        self.task = None

    def add_link(self, link: Link):
        if link not in self.links:
            self.links.append(link)

    def remove_link(self, link: Link):
        if link in self.links:
            self.links.remove(link)

    def register_failure_callback(self, callback: Callable[[Link], None]):
        self.on_failure.append(callback)

    def register_recovery_callback(self, callback: Callable[[Link], None]):
        self.on_recovery.append(callback)

    async def probe_link(self, link: Link):
        if link.state == LinkState.DOWN:
            return

        link.lacp_success()

    async def run(self):
        self.running = True
        while self.running:
            for link in self.links:
                await self.probe_link(link)
            await asyncio.sleep(self.probe_interval)

    def start(self):
        if not self.running:
            self.task = asyncio.create_task(self.run())

    def stop(self):
        self.running = False
        if self.task and not self.task.done():
            self.task.cancel()

    def get_status(self) -> dict:
        status = {
            'running': self.running,
            'link_count': len(self.links),
            'up_count': sum(1 for l in self.links if l.is_up()),
            'down_count': sum(1 for l in self.links if not l.is_up())
        }
        return status
