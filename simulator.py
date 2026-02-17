import asyncio
import time
from node import Node
from link import Link
from topology import Topology
from lacp import LACPDetector
from bpdu import BPDUManager
from stp import STPCalculator
from visualizer import NetworkVisualizer, SimpleVisualizer


class NetworkSimulator:
    def __init__(self):
        self.topology = Topology()
        self.lacp_detector = LACPDetector()
        self.bpdu_manager = BPDUManager()
        self.stp_calculator = STPCalculator(self.topology)
        self.visualizer = None
        self.running = False

    def setup_4_node_full_mesh(self):
        node1 = Node("Node1")
        node2 = Node("Node2")
        node3 = Node("Node3")
        node4 = Node("Node4")

        node1.add_port(1)
        node1.add_port(2)
        node1.add_port(3)
        node2.add_port(1)
        node2.add_port(2)
        node2.add_port(3)
        node3.add_port(1)
        node3.add_port(2)
        node3.add_port(3)
        node4.add_port(1)
        node4.add_port(2)
        node4.add_port(3)

        self.topology.add_node(node1)
        self.topology.add_node(node2)
        self.topology.add_node(node3)
        self.topology.add_node(node4)

        self._connect_nodes(node1, node2, 1, 1, 1000, 1)
        self._connect_nodes(node1, node3, 2, 1, 1000, 1)
        self._connect_nodes(node1, node4, 3, 1, 1000, 1)
        self._connect_nodes(node2, node3, 2, 2, 1000, 1)
        self._connect_nodes(node2, node4, 3, 2, 1000, 1)
        self._connect_nodes(node3, node4, 3, 3, 1000, 1)

        for node in [node1, node2, node3, node4]:
            self.bpdu_manager.add_node(node)

        for link in self.topology.get_all_links():
            self.lacp_detector.add_link(link)

    def _connect_nodes(self, node1: Node, node2: Node, port1_id: int, port2_id: int,
                       bandwidth: float, latency: float):
        port1 = node1.get_port(port1_id)
        port2 = node2.get_port(port2_id)
        if port1 and port2:
            link = Link(port1, port2, bandwidth, latency)
            self.topology.add_link(link)

    def setup_callbacks(self):
        def on_link_failure(link):
            print(f"[事件] 链路故障: {link.link_id}")
            self._recalculate_stp()

        def on_link_recovery(link):
            print(f"[事件] 链路恢复: {link.link_id}")
            self._recalculate_stp()

        def on_topology_change():
            print(f"[事件] 拓扑变更")
            self._recalculate_stp()

        def on_node_failure(node):
            print(f"[事件] 节点故障: {node.node_name}")
            self._recalculate_stp()

        self.lacp_detector.register_failure_callback(on_link_failure)
        self.lacp_detector.register_recovery_callback(on_link_recovery)
        self.bpdu_manager.register_topology_change_callback(on_topology_change)
        self.bpdu_manager.register_node_failure_callback(on_node_failure)

    def _recalculate_stp(self):
        self.stp_calculator.update_and_apply()
        if self.visualizer:
            self.visualizer.draw("动态自愈无环网络")

    def initialize_visualizer(self):
        self.visualizer = NetworkVisualizer(self.topology)

    async def run_simulation(self, duration: float = 30.0):
        print("=" * 60)
        print("基于LACP与BPDU协同探测的动态自愈无环网络仿真")
        print("=" * 60)

        self.setup_4_node_full_mesh()
        self.setup_callbacks()

        self.stp_calculator.update_and_apply()

        self.lacp_detector.start()
        self.bpdu_manager.start()

        if self.visualizer:
            self.visualizer.draw("初始网络拓扑 - 4节点全互联")

        SimpleVisualizer.print_topology_summary(self.topology)

        start_time = time.time()
        self.running = True

        try:
            phase = 0
            while self.running and (time.time() - start_time) < duration:
                elapsed = time.time() - start_time

                if elapsed > 5 and phase == 0:
                    phase = 1
                    print("\n" + "=" * 60)
                    print("测试场景1: 注入链路故障 (Node1-Node2)")
                    print("=" * 60)
                    self.topology.inject_link_failure("Node1", "Node2")
                    await asyncio.sleep(0.1)
                    self._recalculate_stp()
                    SimpleVisualizer.print_topology_summary(self.topology)

                elif elapsed > 12 and phase == 1:
                    phase = 2
                    print("\n" + "=" * 60)
                    print("测试场景2: 链路恢复 (Node1-Node2)")
                    print("=" * 60)
                    self.topology.inject_link_recovery("Node1", "Node2")
                    for link in self.topology.get_all_links():
                        n1, n2 = link.get_connected_nodes()
                        node1 = self.topology.get_node(n1)
                        node2 = self.topology.get_node(n2)
                        if node1 and node2:
                            if (node1.node_name == "Node1" and node2.node_name == "Node2") or \
                               (node1.node_name == "Node2" and node2.node_name == "Node1"):
                                link.lacp_success()
                    await asyncio.sleep(0.1)
                    self._recalculate_stp()
                    SimpleVisualizer.print_topology_summary(self.topology)

                elif elapsed > 20 and phase == 2:
                    phase = 3
                    print("\n" + "=" * 60)
                    print("测试场景3: 注入节点故障 (Node3)")
                    print("=" * 60)
                    self.topology.inject_node_failure("Node3")
                    await asyncio.sleep(0.1)
                    self._recalculate_stp()
                    SimpleVisualizer.print_topology_summary(self.topology)

                if self.visualizer:
                    self.visualizer.show_stats(
                        self.lacp_detector.get_status(),
                        self.bpdu_manager.get_status(),
                        self.stp_calculator.get_spanning_tree_info()
                    )

                await asyncio.sleep(2)

        except KeyboardInterrupt:
            print("\n仿真被用户中断")
        finally:
            self.lacp_detector.stop()
            self.bpdu_manager.stop()
            self.running = False

        print("\n" + "=" * 60)
        print("仿真结束")
        print("=" * 60)

        if self.visualizer:
            print("\n按Ctrl+C或关闭图形窗口退出...")
            try:
                import matplotlib.pyplot as plt
                plt.show(block=True)
            except:
                pass

    def stop(self):
        self.running = False


def main():
    import sys

    simulator = NetworkSimulator()

    if len(sys.argv) > 1 and sys.argv[1] == '--no-gui':
        print("运行无GUI模式")
    else:
        try:
            import matplotlib
            import networkx
            print("初始化可视化...")
            simulator.initialize_visualizer()
        except ImportError as e:
            print(f"警告: 无法加载可视化库: {e}")
            print("将使用无GUI模式")

    try:
        asyncio.run(simulator.run_simulation(duration=30))
    except KeyboardInterrupt:
        print("\n程序退出")


if __name__ == "__main__":
    main()
