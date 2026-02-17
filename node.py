import uuid
from enum import Enum
from typing import Dict, List, Optional
import time


class PortState(Enum):
    DISABLED = "DISABLED"
    BLOCKING = "BLOCKING"
    LISTENING = "LISTENING"
    LEARNING = "LEARNING"
    FORWARDING = "FORWARDING"


class NodeState(Enum):
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"


class Port:
    def __init__(self, port_id: int, node_id: str):
        self.port_id = port_id
        self.node_id = node_id
        self.state = PortState.DISABLED
        self.link: Optional['Link'] = None
        self.mac_table: Dict[str, str] = {}
        self.last_bpdu_time = 0.0
        self.bpdu_count = 0

    def connect_link(self, link: 'Link'):
        self.link = link
        self.state = PortState.BLOCKING

    def disconnect_link(self):
        self.link = None
        self.state = PortState.DISABLED

    def update_state(self, new_state: PortState):
        self.state = new_state

    def record_bpdu(self):
        self.last_bpdu_time = time.time()
        self.bpdu_count += 1


class Node:
    def __init__(self, node_name: str):
        self.node_id = str(uuid.uuid4())[:8]
        self.node_name = node_name
        self.state = NodeState.ACTIVE
        self.ports: Dict[int, Port] = {}
        self.is_root = False
        self.root_id: Optional[str] = None
        self.root_path_cost = 0
        self.parent_port: Optional[Port] = None
        self.last_heartbeat = time.time()

    def add_port(self, port_id: int):
        if port_id not in self.ports:
            self.ports[port_id] = Port(port_id, self.node_id)
        return self.ports[port_id]

    def get_port(self, port_id: int) -> Optional[Port]:
        return self.ports.get(port_id)

    def get_active_ports(self) -> List[Port]:
        return [p for p in self.ports.values() if p.state != PortState.DISABLED]

    def get_forwarding_ports(self) -> List[Port]:
        return [p for p in self.ports.values() if p.state == PortState.FORWARDING]

    def set_failed(self):
        self.state = NodeState.FAILED
        for port in self.ports.values():
            port.state = PortState.DISABLED

    def set_active(self):
        self.state = NodeState.ACTIVE
        self.last_heartbeat = time.time()

    def update_heartbeat(self):
        self.last_heartbeat = time.time()

    def is_alive(self, timeout: float = 5.0) -> bool:
        if self.state == NodeState.FAILED:
            return False
        return (time.time() - self.last_heartbeat) < timeout

    def to_dict(self) -> Dict:
        return {
            'node_id': self.node_id,
            'node_name': self.node_name,
            'state': self.state.value,
            'is_root': self.is_root,
            'ports': {
                pid: {
                    'state': p.state.value,
                    'has_link': p.link is not None
                } for pid, p in self.ports.items()
            }
        }
