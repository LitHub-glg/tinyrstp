import asyncio
import time
import struct
from typing import Dict, List, Optional, Callable
from node import Node, Port, PortState, NodeState


class BPDU:
    PROTOCOL_ID = 0xC001

    def __init__(
        self,
        root_id: str,
        sender_id: str,
        port_id: int,
        cost: int,
        age: float = 0.0,
        max_age: float = 20.0,
        hello_time: float = 2.0,
        flags: int = 0
    ):
        self.protocol_id = self.PROTOCOL_ID
        self.root_id = root_id
        self.sender_id = sender_id
        self.port_id = port_id
        self.cost = cost
        self.age = age
        self.max_age = max_age
        self.hello_time = hello_time
        self.flags = flags
        self.timestamp = time.time()

    def pack(self) -> bytes:
        root_bytes = self.root_id.encode('utf-8')[:8].ljust(8, b'\x00')
        sender_bytes = self.sender_id.encode('utf-8')[:8].ljust(8, b'\x00')
        return struct.pack(
            '!H8s8sHIfIIB',
            self.protocol_id,
            root_bytes,
            sender_bytes,
            self.port_id,
            self.cost,
            self.age,
            int(self.max_age),
            int(self.hello_time),
            self.flags
        )

    @classmethod
    def unpack(cls, data: bytes) -> Optional['BPDU']:
        try:
            unpacked = struct.unpack('!H8s8sHIfIIB', data)
            proto_id = unpacked[0]
            if proto_id != cls.PROTOCOL_ID:
                return None
            return cls(
                root_id=unpacked[1].rstrip(b'\x00').decode('utf-8'),
                sender_id=unpacked[2].rstrip(b'\x00').decode('utf-8'),
                port_id=unpacked[3],
                cost=unpacked[4],
                age=unpacked[5],
                max_age=float(unpacked[6]),
                hello_time=float(unpacked[7]),
                flags=unpacked[8]
            )
        except Exception:
            return None

    def is_expired(self) -> bool:
        return (time.time() - self.timestamp) > self.max_age


class BPDUManager:
    def __init__(self, hello_interval: float = 0.5, max_age: float = 3.0):
        self.hello_interval = hello_interval
        self.max_age = max_age
        self.nodes: Dict[str, Node] = {}
        self.running = False
        self.on_topology_change: List[Callable[[], None]] = []
        self.on_node_failure: List[Callable[[Node], None]] = []
        self.task: Optional[asyncio.Task] = None
        self.last_bpdu_received: Dict[str, float] = {}

    def add_node(self, node: Node):
        self.nodes[node.node_id] = node
        self.last_bpdu_received[node.node_id] = time.time()

    def register_topology_change_callback(self, callback: Callable[[], None]):
        self.on_topology_change.append(callback)

    def register_node_failure_callback(self, callback: Callable[[Node], None]):
        self.on_node_failure.append(callback)

    def send_bpdu(self, node: Node, port: Port):
        if node.state != NodeState.ACTIVE:
            return
        if not port.link or not port.link.is_up():
            return

        bpdu = BPDU(
            root_id=node.root_id or node.node_id,
            sender_id=node.node_id,
            port_id=port.port_id,
            cost=node.root_path_cost,
            max_age=self.max_age,
            hello_time=self.hello_interval
        )

        other_port = port.link.get_other_port(port)
        if other_port:
            self.receive_bpdu(other_port, bpdu)

    def receive_bpdu(self, port: Port, bpdu: BPDU):
        port.record_bpdu()
        self.last_bpdu_received[bpdu.sender_id] = time.time()

        node = self._find_node_by_port(port)
        if not node:
            return

        self._process_bpdu(node, port, bpdu)

    def _find_node_by_port(self, port: Port) -> Optional[Node]:
        for node in self.nodes.values():
            if port in node.ports.values():
                return node
        return None

    def _process_bpdu(self, node: Node, port: Port, bpdu: BPDU):
        if node.root_id is None:
            node.root_id = bpdu.root_id
            self._trigger_topology_change()
            return

        current_root_priority = self._get_node_priority(node.root_id)
        new_root_priority = self._get_node_priority(bpdu.root_id)

        if new_root_priority < current_root_priority:
            node.root_id = bpdu.root_id
            node.root_path_cost = bpdu.cost + 1
            node.parent_port = port
            self._trigger_topology_change()
        elif bpdu.root_id == node.root_id:
            new_cost = bpdu.cost + 1
            if new_cost < node.root_path_cost:
                node.root_path_cost = new_cost
                node.parent_port = port
                self._trigger_topology_change()
            elif new_cost == node.root_path_cost:
                if bpdu.sender_id < node.node_id:
                    node.parent_port = port
                    self._trigger_topology_change()

    def _get_node_priority(self, node_id: str) -> int:
        return int(node_id, 16) if node_id else 0xFFFF

    def _trigger_topology_change(self):
        for callback in self.on_topology_change:
            try:
                callback()
            except Exception as e:
                print(f"Topology change callback error: {e}")

    def _check_node_alive(self, node: Node):
        if node.state == NodeState.FAILED:
            return
        last_time = self.last_bpdu_received.get(node.node_id, 0)
        if (time.time() - last_time) > self.max_age:
            node.set_failed()
            for callback in self.on_node_failure:
                try:
                    callback(node)
                except Exception as e:
                    print(f"Node failure callback error: {e}")
            self._trigger_topology_change()

    async def run(self):
        self.running = True
        while self.running:
            for node in self.nodes.values():
                if node.state == NodeState.ACTIVE:
                    for port in node.ports.values():
                        if port.link and port.link.is_up():
                            self.send_bpdu(node, port)
                self._check_node_alive(node)

            await asyncio.sleep(self.hello_interval)

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
            'node_count': len(self.nodes),
            'active_nodes': sum(1 for n in self.nodes.values() if n.state == NodeState.ACTIVE),
            'failed_nodes': sum(1 for n in self.nodes.values() if n.state == NodeState.FAILED)
        }
        return status
