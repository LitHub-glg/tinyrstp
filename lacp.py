import asyncio
import time
from typing import List, Callable
from link import Link, LinkState


class LACPDetector:
    def __init__(self, probe_interval: float = 0.01, timeout: float = 0.03):
        self.probe_interval = probe_interval
        self.timeout = timeout
        self.links: List[Link] = []
        self.running = False
        self.on_failure: List[Callable[[Link], None]] = []
        self.on_recovery: List[Callable[[Link], None]] = []
        self.task: Optional[asyncio.Task] = None

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

        current_time = time.time()
        time_since_last = current_time - link.last_lacp_time

        if time_since_last > self.timeout:
            old_state = link.state
            link.lacp_fail()
            if link.state == LinkState.DOWN and old_state != LinkState.DOWN:
                for callback in self.on_failure:
                    try:
                        callback(link)
                    except Exception as e:
                        print(f"Failure callback error: {e}")
        else:
            old_state = link.state
            link.lacp_success()
            if link.state == LinkState.UP and old_state != LinkState.UP:
                for callback in self.on_recovery:
                    try:
                        callback(link)
                    except Exception as e:
                        print(f"Recovery callback error: {e}")

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
