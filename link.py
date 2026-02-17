from enum import Enum
import time
from typing import Optional, Tuple
from node import Port


class LinkState(Enum):
    UP = "UP"
    DOWN = "DOWN"
    DEGRADED = "DEGRADED"


class Link:
    def __init__(self, port1: Port, port2: Port, bandwidth: float = 1000.0, latency: float = 1.0):
        self.link_id = f"{port1.node_id}-{port1.port_id}<->{port2.node_id}-{port2.port_id}"
        self.port1 = port1
        self.port2 = port2
        self.state = LinkState.UP
        self.bandwidth = bandwidth
        self.latency = latency
        self.last_lacp_time = time.time()
        self.lacp_fail_count = 0
        self.lacp_success_count = 0
        self.created_at = time.time()

        port1.connect_link(self)
        port2.connect_link(self)

    def get_other_port(self, port: Port) -> Optional[Port]:
        if port == self.port1:
            return self.port2
        elif port == self.port2:
            return self.port1
        return None

    def get_connected_nodes(self) -> Tuple[str, str]:
        return (self.port1.node_id, self.port2.node_id)

    def lacp_success(self):
        self.lacp_success_count += 1
        self.lacp_fail_count = 0
        self.last_lacp_time = time.time()
        if self.state != LinkState.UP:
            self.state = LinkState.UP

    def lacp_fail(self):
        self.lacp_fail_count += 1
        if self.lacp_fail_count >= 3:
            self.state = LinkState.DOWN

    def set_state(self, new_state: LinkState):
        self.state = new_state
        if new_state == LinkState.DOWN:
            self.lacp_fail_count = 3
        elif new_state == LinkState.UP:
            self.lacp_fail_count = 0
            self.lacp_success_count += 1

    def is_up(self) -> bool:
        return self.state == LinkState.UP

    def get_cost(self) -> float:
        if not self.is_up():
            return float('inf')
        return (1.0 / self.bandwidth) * 1000 + self.latency

    def to_dict(self) -> dict:
        return {
            'link_id': self.link_id,
            'state': self.state.value,
            'bandwidth': self.bandwidth,
            'latency': self.latency,
            'lacp_fail_count': self.lacp_fail_count,
            'nodes': self.get_connected_nodes()
        }

    def disconnect(self):
        self.port1.disconnect_link()
        self.port2.disconnect_link()
        self.state = LinkState.DOWN
