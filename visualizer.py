import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from typing import Dict, List, Optional, Tuple
from topology import Topology
from node import NodeState, PortState
from link import LinkState
import time


class NetworkVisualizer:
    def __init__(self, topology: Topology):
        self.topology = topology
        self.fig = None
        self.ax = None
        self.pos = None
        self.last_update = 0

    def _setup_layout(self):
        nodes = self.topology.get_all_nodes()
        node_names = [n.node_name for n in nodes]
        positions = {}

        layout_4 = {
            'Node1': (-1, 1),
            'Node2': (1, 1),
            'Node3': (-1, -1),
            'Node4': (1, -1)
        }

        for node in nodes:
            if node.node_name in layout_4:
                positions[node.node_id] = layout_4[node.node_name]
            else:
                import random
                positions[node.node_id] = (random.uniform(-2, 2), random.uniform(-2, 2))

        self.pos = positions

    def _get_node_color(self, node):
        if node.state == NodeState.FAILED:
            return '#ff4444'
        if node.is_root:
            return '#44ff44'
        return '#4488ff'

    def _get_link_color(self, link, is_st: bool):
        if link.state == LinkState.DOWN:
            return '#888888'
        if is_st:
            return '#44ff44'
        return '#cccccc'

    def _get_link_width(self, link, is_st: bool):
        if link.state == LinkState.DOWN:
            return 1
        if is_st:
            return 4
        return 2

    def draw(self, title: str = "网络拓扑", block: bool = False):
        if self.fig is None:
            self.fig, self.ax = plt.subplots(figsize=(10, 8))
            self._setup_layout()
        else:
            self.ax.clear()

        G = nx.Graph()

        node_labels = {}
        node_colors = []
        for node in self.topology.get_all_nodes():
            G.add_node(node.node_id)
            status = "✓" if node.state == NodeState.ACTIVE else "✗"
            root = " (根)" if node.is_root else ""
            node_labels[node.node_id] = f"{node.node_name}\n{status}{root}"
            node_colors.append(self._get_node_color(node))

        edge_colors = []
        edge_widths = []
        st_links = self.topology.spanning_tree_links
        for link in self.topology.get_all_links():
            n1_id, n2_id = link.get_connected_nodes()
            G.add_edge(n1_id, n2_id)
            is_st = link.link_id in st_links
            edge_colors.append(self._get_link_color(link, is_st))
            edge_widths.append(self._get_link_width(link, is_st))

        nx.draw_networkx_nodes(G, self.pos, ax=self.ax, node_color=node_colors,
                               node_size=3000, edgecolors='black', linewidths=2)
        nx.draw_networkx_edges(G, self.pos, ax=self.ax, edge_color=edge_colors,
                               width=edge_widths)
        nx.draw_networkx_labels(G, self.pos, node_labels, ax=self.ax,
                                font_size=12, font_weight='bold')

        self._draw_legend()

        self.ax.set_title(title, fontsize=16, fontweight='bold')
        self.ax.axis('off')

        self.last_update = time.time()

        if block:
            plt.show()
        else:
            plt.draw()
            plt.pause(0.01)

    def _draw_legend(self):
        legend_elements = [
            mpatches.Patch(color='#4488ff', label='正常节点'),
            mpatches.Patch(color='#44ff44', label='根节点'),
            mpatches.Patch(color='#ff4444', label='故障节点'),
            mpatches.Patch(color='#44ff44', label='生成树链路'),
            mpatches.Patch(color='#cccccc', label='备用链路'),
            mpatches.Patch(color='#888888', label='故障链路')
        ]
        self.ax.legend(handles=legend_elements, loc='upper right',
                      bbox_to_anchor=(1.3, 1))

    def show_stats(self, lacp_status: Dict, bpdu_status: Dict, stp_info: Dict):
        print("\n" + "=" * 60)
        print("网络状态监控")
        print("=" * 60)
        print(f"LACP 探测器: {'运行中' if lacp_status['running'] else '停止'}")
        print(f"  - 总链路数: {lacp_status['link_count']}")
        print(f"  - 正常链路: {lacp_status['up_count']}")
        print(f"  - 故障链路: {lacp_status['down_count']}")
        print()
        print(f"BPDU 管理器: {'运行中' if bpdu_status['running'] else '停止'}")
        print(f"  - 总节点数: {bpdu_status['node_count']}")
        print(f"  - 正常节点: {bpdu_status['active_nodes']}")
        print(f"  - 故障节点: {bpdu_status['failed_nodes']}")
        print()
        print("生成树状态:")
        print(f"  - 根节点: {stp_info['root_node']}")
        print(f"  - 节点数: {stp_info['node_count']}")
        print(f"  - 链路数: {stp_info['link_count']}")
        print("=" * 60 + "\n")

    def close(self):
        if self.fig:
            plt.close(self.fig)
            self.fig = None


class SimpleVisualizer:
    @staticmethod
    def print_topology_summary(topology: Topology):
        print("\n=== 网络拓扑摘要 ===")
        print(f"\n节点 ({len(topology.get_all_nodes())}):")
        for node in topology.get_all_nodes():
            status = "ACTIVE" if node.state == NodeState.ACTIVE else "FAILED"
            root = " [ROOT]" if node.is_root else ""
            fw_ports = len(node.get_forwarding_ports())
            print(f"  {node.node_name}: {status}{root}, 转发端口: {fw_ports}")

        print(f"\n链路 ({len(topology.get_all_links())}):")
        st_links = topology.spanning_tree_links
        for link in topology.get_all_links():
            n1_id, n2_id = link.get_connected_nodes()
            n1 = topology.get_node(n1_id)
            n2 = topology.get_node(n2_id)
            status = "UP" if link.is_up() else "DOWN"
            st = " [ST]" if link.link_id in st_links else ""
            print(f"  {n1.node_name if n1 else '?'} <-> {n2.node_name if n2 else '?'}: {status}{st}")
        print("===================\n")
