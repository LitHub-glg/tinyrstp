import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from frontend.gui.client import APIClient
from frontend.gui.main import NetworkGUI

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def test_gui():
    print("=" * 60)
    print("GUI功能测试")
    print("=" * 60)
    
    client = APIClient()
    
    try:
        print("\n1. 创建GUI实例...")
        gui = NetworkGUI(client)
        print("   ✓ GUI实例创建成功")
        
        print("\n2. 初始化GUI...")
        gui.setup()
        print("   ✓ GUI初始化成功")
        
        print("\n3. 连接后端API...")
        gui._refresh_topology()
        print("   ✓ 数据获取成功")
        print(f"   节点数量: {len(gui.topology_data.get('nodes', {}))}")
        print(f"   链路数量: {len(gui.topology_data.get('links', {}))}")
        print(f"   位置数量: {len(gui.pos)}")
        
        print("\n4. 绘制图形...")
        gui.draw()
        print("   ✓ 图形绘制成功")
        
        print("\n5. 保存图形到文件...")
        plt.savefig('/tmp/gui_test.png', dpi=100, bbox_inches='tight')
        print("   ✓ 图形已保存到 /tmp/gui_test.png")
        
        print("\n" + "=" * 60)
        print("所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_gui()
