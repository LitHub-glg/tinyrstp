import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import matplotlib

print("检测可用的matplotlib后端...")
backends_to_try = ['MacOSX', 'TkAgg', 'Qt5Agg', 'QtAgg', 'Agg']
working_backend = None

for backend in backends_to_try:
    try:
        matplotlib.use(backend, force=True)
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1, 1))
        plt.close(fig)
        working_backend = backend
        print(f"   ✓ {backend} 可用")
        break
    except Exception as e:
        print(f"   ✗ {backend} 不可用: {e}")
        continue

if not working_backend:
    print("错误: 没有可用的交互式后端")
    sys.exit(1)

print(f"\n使用后端: {working_backend}")
matplotlib.use(working_backend, force=True)

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from frontend.gui.client import APIClient

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

print("\n" + "=" * 60)
print("GUI诊断测试")
print("=" * 60)

try:
    print("\n1. 测试matplotlib图形创建...")
    fig, ax = plt.subplots(figsize=(10, 8))
    print("   ✓ 图形创建成功")
    
    print("\n2. 测试API连接...")
    client = APIClient()
    print(f"   API URL: {client.base_url}")
    
    print("\n3. 获取拓扑数据...")
    topology_data = client.get_topology()
    print(f"   节点数量: {len(topology_data.get('nodes', {}))}")
    print(f"   链路数量: {len(topology_data.get('links', {}))}")
    print(f"   生成树链路: {len(topology_data.get('spanning_tree', []))}")
    print("   ✓ 数据获取成功")
    
    print("\n4. 测试网络图绘制...")
    
    G = nx.Graph()
    
    layout_by_name = {
        'Node1': (-1, 1),
        'Node2': (1, 1),
        'Node3': (-1, -1),
        'Node4': (1, -1)
    }
    
    pos = {}
    for node_id, node_data in topology_data.get('nodes', {}).items():
        node_name = node_data.get('node_name', '')
        G.add_node(node_id)
        if node_name in layout_by_name:
            pos[node_id] = layout_by_name[node_name]
    
    for link_id, link_data in topology_data.get('links', {}).items():
        nodes = link_data.get('nodes', [])
        if len(nodes) >= 2:
            G.add_edge(nodes[0], nodes[1])
    
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color='#4488ff', node_size=3500, edgecolors='black', linewidths=2)
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#cccccc', width=2)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=12, font_weight='bold')
    
    ax.set_title("Network Topology Test", fontsize=14, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    
    print("   ✓ 网络图绘制成功")
    
    print("\n5. 显示图形...")
    print(f"   后端: {matplotlib.get_backend()}")
    print("   图形窗口应该已经打开")
    
    plt.show()
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
