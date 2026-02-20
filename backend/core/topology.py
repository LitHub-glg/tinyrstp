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

    def check_connectivity_to_root(self, node: Node) -> dict:
        """
        Check if a node can reach the root node.
        Returns dict with 'reachable', 'path', and 'blocked_by' keys.
        """
        if not self.root_node:
            return {'reachable': False, 'path': [], 'blocked_by': 'no_root'}
        
        if node.id == self.root_node.id:
            return {'reachable': True, 'path': [], 'blocked_by': None}
        
        if node.state == NodeState.FAILED:
            return {'reachable': False, 'path': [], 'blocked_by': 'node_failed'}
        
        visited = set()
        queue = [(node.id, [])]
        
        while queue:
            current_id, path = queue.pop(0)
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            if current_id == self.root_node.id:
                return {'reachable': True, 'path': path, 'blocked_by': None}
            
            current_node = self.nodes.get(current_id)
            if not current_node or current_node.state == NodeState.FAILED:
                continue
            
            for link in self.links.values():
                n1_id, n2_id = link.get_connected_nodes()
                
                neighbor_id = None
                if n1_id == current_id and n2_id not in visited:
                    neighbor_id = n2_id
                elif n2_id == current_id and n1_id not in visited:
                    neighbor_id = n1_id
                
                if neighbor_id:
                    neighbor_node = self.nodes.get(neighbor_id)
                    
                    if not link.is_up():
                        continue
                    
                    if neighbor_node and neighbor_node.state == NodeState.ACTIVE:
                        new_path = path + [{
                            'link_id': link.link_id,
                            'link_state': link.state.value,
                            'from_node': current_id,
                            'to_node': neighbor_id
                        }]
                        queue.append((neighbor_id, new_path))
        
        return {'reachable': False, 'path': [], 'blocked_by': 'no_path'}
    
    def get_all_connectivity(self) -> dict:
        """
        Get connectivity status for all nodes to the root.
        """
        connectivity = {}
        for node_id, node in self.nodes.items():
            if node.id != (self.root_node.id if self.root_node else None):
                connectivity[node_id] = self.check_connectivity_to_root(node)
        return connectivity
    
    def to_dict(self) -> dict:
        connectivity = self.get_all_connectivity()
        
        nodes_dict = {}
        for n in self.nodes.values():
            node_data = n.to_dict()
            if n.id in connectivity:
                node_data['connectivity'] = connectivity[n.id]
            elif self.root_node and n.id == self.root_node.id:
                node_data['connectivity'] = {'reachable': True, 'path': [], 'blocked_by': None, 'is_root': True}
            else:
                node_data['connectivity'] = {'reachable': False, 'path': [], 'blocked_by': 'no_root'}
            nodes_dict[n.id] = node_data
        
        return {
            'nodes': nodes_dict,
            'links': {l.link_id: l.to_dict() for l in self.links.values()},
            'spanning_tree': list(self.spanning_tree_links),
            'root_node': self.root_node.id if self.root_node else None,
            'last_update': self.last_update_time,
            'connectivity_summary': {
                'total_nodes': len(self.nodes),
                'reachable_nodes': sum(1 for c in connectivity.values() if c['reachable']),
                'unreachable_nodes': sum(1 for c in connectivity.values() if not c['reachable'])
            }
        }
