import heapq
from typing import Set
from backend.core.topology import Topology
from backend.core.node import Node, PortState
from backend.core.link import Link


class STPCalculator:
    def __init__(self, topology: Topology):
        self.topology = topology

    def calculate_spanning_tree(self) -> Set[str]:
        self.topology.elect_root()
        if not self.topology.root_node:
            return set()

        st_links = self._prim_mst()
        return st_links

    def _prim_mst(self) -> Set[str]:
        root = self.topology.root_node
        if not root:
            return set()

        active_nodes = self.topology.get_active_nodes()
        if not active_nodes:
            return set()

        node_id_set = {n.node_id for n in active_nodes}
        visited = {root.node_id}
        mst_links = set()

        edge_heap = []

        neighbors = self.topology.get_neighbors(root)
        for neighbor, link in neighbors:
            if neighbor.node_id in node_id_set:
                cost = link.get_cost()
                heapq.heappush(edge_heap, (cost, link.link_id, root.node_id, neighbor.node_id))

        while edge_heap and len(visited) < len(node_id_set):
            cost, link_id, from_id, to_id = heapq.heappop(edge_heap)

            if to_id in visited:
                continue

            link = self.topology.get_link(link_id)
            if not link or not link.is_up():
                continue

            visited.add(to_id)
            mst_links.add(link_id)

            to_node = self.topology.get_node(to_id)
            if to_node:
                new_neighbors = self.topology.get_neighbors(to_node)
                for new_neighbor, new_link in new_neighbors:
                    new_neighbor_id = new_neighbor.node_id
                    if new_neighbor_id not in visited and new_neighbor_id in node_id_set:
                        new_cost = new_link.get_cost()
                        heapq.heappush(
                            edge_heap,
                            (new_cost, new_link.link_id, to_id, new_neighbor_id)
                        )

        return mst_links

    def update_and_apply(self):
        st_links = self.calculate_spanning_tree()
        self.topology.update_spanning_tree(st_links)
        return st_links

    def get_spanning_tree_info(self) -> dict:
        st_links = self.topology.spanning_tree_links
        info = {
            'root_node': self.topology.root_node.node_name if self.topology.root_node else None,
            'link_count': len(st_links),
            'node_count': len(self.topology.get_active_nodes()),
            'links': list(st_links)
        }
        return info
