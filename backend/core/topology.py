from typing import Dict, List, Optional, Set, Tuple
import time
from backend.core.node import Node, NodeState, PortState
from backend.core.link import Link, LinkState


class Topology:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.links: Dict[str, Link] = {}
        self.spanning_tree_links: Set[str] = set()
        self.root_node: Optional[Node] = None
        self.last_update_time = time.time()

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def get_node_by_name(self, name: str) -> Optional[Node]:
        for node in self.nodes.values():
            if node.node_name == name:
                return node
        return None

    def add_link(self, link: Link):
        self.links[link.link_id] = link

    def remove_link(self, link: Link):
        if link.link_id in self.links:
            del self.links[link.link_id]

    def get_link(self, link_id: str) -> Optional[Link]:
        return self.links.get(link_id)

    def get_active_links(self) -> List[Link]:
        return [l for l in self.links.values() if l.is_up()]

    def get_all_links(self) -> List[Link]:
        return list(self.links.values())

    def get_all_nodes(self) -> List[Node]:
        return list(self.nodes.values())

    def get_active_nodes(self) -> List[Node]:
        return [n for n in self.nodes.values() if n.state == NodeState.ACTIVE]

    def get_neighbors(self, node: Node) -> List[Tuple[Node, Link]]:
        neighbors = []
        for link in self.links.values():
            if not link.is_up():
                continue
            n1_id, n2_id = link.get_connected_nodes()
            if node.id == n1_id:
                neighbor = self.nodes.get(n2_id)
                if neighbor and neighbor.state == NodeState.ACTIVE:
                    neighbors.append((neighbor, link))
            elif node.id == n2_id:
                neighbor = self.nodes.get(n1_id)
                if neighbor and neighbor.state == NodeState.ACTIVE:
                    neighbors.append((neighbor, link))
        return neighbors

    def get_node_links(self, node: Node) -> List[Link]:
        node_links = []
        for link in self.links.values():
            n1_id, n2_id = link.get_connected_nodes()
            if node.id in (n1_id, n2_id):
                node_links.append(link)
        return node_links

    def elect_root(self):
        active_nodes = self.get_active_nodes()
        if not active_nodes:
            self.root_node = None
            return

        def get_priority(node: Node) -> int:
            try:
                return int(node.id.split('_')[1])
            except (IndexError, ValueError):
                return 0

        self.root_node = min(active_nodes, key=get_priority)
        self.root_node.is_root = True
        self.root_node.root_id = self.root_node.id
        self.root_node.root_path_cost = 0

        for node in active_nodes:
            if node != self.root_node:
                node.is_root = False

    def update_spanning_tree(self, st_links: Set[str]):
        self.spanning_tree_links = st_links
        self.last_update_time = time.time()

        for node in self.nodes.values():
            for port in node.ports.values():
                if port.link:
                    if port.link.link_id in st_links:
                        if port.state != PortState.FORWARDING:
                            port.update_state(PortState.FORWARDING)
                    else:
                        if port.state != PortState.BLOCKING:
                            port.update_state(PortState.BLOCKING)

    def inject_link_failure(self, node1_name: str, node2_name: str) -> bool:
        n1 = self.get_node_by_name(node1_name)
        n2 = self.get_node_by_name(node2_name)
        if not n1 or not n2:
            return False

        for link in self.links.values():
            ids = link.get_connected_nodes()
            if (n1.id in ids and n2.id in ids):
                link.set_state(LinkState.DOWN)
                return True
        return False

    def inject_link_recovery(self, node1_name: str, node2_name: str) -> bool:
        n1 = self.get_node_by_name(node1_name)
        n2 = self.get_node_by_name(node2_name)
        if not n1 or not n2:
            return False

        for link in self.links.values():
            ids = link.get_connected_nodes()
            if (n1.id in ids and n2.id in ids):
                link.set_state(LinkState.UP)
                return True
        return False

    def inject_node_failure(self, node_name: str) -> bool:
        node = self.get_node_by_name(node_name)
        if node:
            node.set_failed()
            return True
        return False

    def inject_node_recovery(self, node_name: str) -> bool:
        node = self.get_node_by_name(node_name)
        if node:
            node.set_active()
            return True
        return False

    def to_dict(self) -> dict:
        return {
            'nodes': {n.id: n.to_dict() for n in self.nodes.values()},
            'links': {l.link_id: l.to_dict() for l in self.links.values()},
            'spanning_tree': list(self.spanning_tree_links),
            'root_node': self.root_node.id if self.root_node else None,
            'last_update': self.last_update_time
        }
