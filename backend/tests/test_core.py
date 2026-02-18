import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.core.node import Node, NodeState, PortState
from backend.core.link import Link, LinkState


class TestNode:
    def test_node_creation(self):
        node = Node("TestNode")
        assert node.node_name == "TestNode"
        assert node.state == NodeState.ACTIVE
        assert node.is_root == False

    def test_add_port(self):
        node = Node("TestNode")
        port = node.add_port(1)
        assert port is not None
        assert port.port_id == 1
        assert port.node_id == node.node_id

    def test_set_failed(self):
        node = Node("TestNode")
        node.add_port(1)
        node.set_failed()
        assert node.state == NodeState.FAILED
        assert node.ports[1].state == PortState.DISABLED

    def test_set_active(self):
        node = Node("TestNode")
        node.set_failed()
        node.set_active()
        assert node.state == NodeState.ACTIVE


class TestLink:
    def test_link_creation(self):
        node1 = Node("Node1")
        node2 = Node("Node2")
        node1.add_port(1)
        node2.add_port(1)
        link = Link(node1.get_port(1), node2.get_port(1), 1000, 1)
        assert link.bandwidth == 1000
        assert link.latency == 1
        assert link.state == LinkState.UP

    def test_link_down(self):
        node1 = Node("Node1")
        node2 = Node("Node2")
        node1.add_port(1)
        node2.add_port(1)
        link = Link(node1.get_port(1), node2.get_port(1), 1000, 1)
        link.set_state(LinkState.DOWN)
        assert link.state == LinkState.DOWN
        assert link.lacp_fail_count == 3

    def test_link_up(self):
        node1 = Node("Node1")
        node2 = Node("Node2")
        node1.add_port(1)
        node2.add_port(1)
        link = Link(node1.get_port(1), node2.get_port(1), 1000, 1)
        link.set_state(LinkState.DOWN)
        link.set_state(LinkState.UP)
        assert link.state == LinkState.UP
        assert link.lacp_fail_count == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
