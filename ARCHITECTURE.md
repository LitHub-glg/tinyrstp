# 前后端分离架构设计

## 项目结构

```
solo_cpc/
├── backend/                    # 后端服务
│   ├── core/                 # 核心业务逻辑
│   │   ├── node.py           # 节点类
│   │   ├── link.py           # 链路类
│   │   ├── topology.py       # 拓扑管理
│   │   ├── stp.py           # 生成树计算
│   │   ├── lacp.py          # LACP探测
│   │   └── bpdu.py          # BPDU协议
│   ├── api/                  # API接口层
│   │   └── app.py           # Flask应用（包含路由定义）
│   ├── tests/                # 后端测试
│   │   ├── test_core.py      # 核心逻辑测试（7个测试用例）
│   │   └── test_api.py       # API接口测试（14个测试用例）
│   └── main.py              # 后端启动入口
│
├── frontend/                 # 前端应用
│   ├── gui/                 # GUI界面
│   │   ├── main.py          # 主界面（包含可视化组件）
│   │   └── client.py       # API客户端（打桩接口）
│   ├── tests/                # 前端测试
│   │   ├── test_client.py   # 客户端测试（16个测试用例）
│   │   └── test_gui.py      # GUI组件测试（14个测试用例）
│   ├── debug_gui.py         # GUI调试工具
│   ├── test_gui_offline.py  # GUI离线测试
│   └── main.py              # 前端启动入口
│
├── requirements.txt           # 依赖包
├── README.md               # 项目说明
└── ARCHITECTURE.md         # 本文件
```

## 架构设计

### 1. 后端架构

```
┌─────────────────────────────────────────┐
│         Backend Service              │
├─────────────────────────────────────────┤
│                                   │
│  ┌─────────────────────────────┐    │
│  │   API Layer (Flask)      │    │
│  │   - REST API             │    │
│  │   - JSON Response         │    │
│  │   - Route Definitions    │    │
│  └──────────┬──────────────────┘    │
│             │                         │
│  ┌──────────▼──────────────────┐    │
│  │   Core Business Logic      │    │
│  │   - Node Management       │    │
│  │   - Link Management      │    │
│  │   - Topology Control     │    │
│  │   - STP Calculation     │    │
│  │   - LACP Detection      │    │
│  │   - BPDU Protocol       │    │
│  └────────────────────────────┘    │
│                                   │
│  ┌─────────────────────────────┐    │
│  │   Test Suite              │    │
│  │   - Unit Tests (7)        │    │
│  │   - Integration Tests (14) │    │
│  └────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### 2. 前端架构

```
┌─────────────────────────────────────────┐
│         Frontend Application         │
├─────────────────────────────────────────┤
│                                   │
│  ┌─────────────────────────────┐    │
│  │   GUI Layer              │    │
│  │   - Network Visualization  │    │
│  │   - Control Panel        │    │
│  │   - Info Display        │    │
│  │   - Interactive Buttons  │    │
│  └──────────┬──────────────────┘    │
│             │                         │
│  ┌──────────▼──────────────────┐    │
│  │   Client Layer (Stub)      │    │
│  │   - API Client           │    │
│  │   - Mock Interface      │    │
│  │   - Test Automation     │    │
│  └──────────┬──────────────────┘    │
│             │                         │
│  ┌──────────▼──────────────────┐    │
│  │   Test Suite              │    │
│  │   - GUI Tests (14)        │    │
│  │   - Client Tests (16)     │    │
│  │   - E2E Tests            │    │
│  └────────────────────────────┘    │
└─────────────────────────────────────────┘
```

## API接口设计

### 拓扑管理接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/topology | 获取完整拓扑 |
| POST | /api/topology/reset | 重置拓扑 |
| GET | /api/topology/nodes | 获取所有节点 |
| GET | /api/topology/links | 获取所有链路 |
| GET | /api/topology/spanning-tree | 获取生成树 |

### 节点操作接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/nodes/{node_id}/fail | 注入节点故障 |
| POST | /api/nodes/{node_id}/recover | 恢复节点 |

### 链路操作接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/links/{link_id}/toggle | 切换链路状态 |
| POST | /api/links/{link_id}/up | 链路UP |
| POST | /api/links/{link_id}/down | 链路DOWN |

### 测试接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/test/scenario/{name} | 执行测试场景 |
| GET | /api/test/status | 获取测试状态 |

## 测试策略

### 后端测试

1. **单元测试**：测试核心业务逻辑（test_core.py）
   - Node类测试（4个测试用例）
   - Link类测试（3个测试用例）
   - 总计：7个测试用例

2. **集成测试**：测试API接口（test_api.py）
   - 拓扑管理API（5个测试用例）
   - 节点操作API（2个测试用例）
   - 链路操作API（3个测试用例）
   - 测试场景API（4个测试用例）
   - 总计：14个测试用例

**后端总计**：21个测试用例

### 前端测试

1. **客户端测试**：测试API客户端和自动化场景（test_client.py）
   - API客户端方法测试（12个测试用例）
   - 自动化场景测试（4个测试用例）
   - 总计：16个测试用例

2. **GUI组件测试**：测试GUI组件（test_gui.py）
   - GUI初始化测试（2个测试用例）
   - GUI按钮测试（2个测试用例）
   - GUI功能测试（10个测试用例）
   - 总计：14个测试用例

**前端总计**：30个测试用例

### 测试覆盖

| 模块 | 测试文件 | 测试用例数 | 状态 |
|------|---------|----------|------|
| 后端核心逻辑 | test_core.py | 7 | ✅ 全部通过 |
| 后端API接口 | test_api.py | 14 | ✅ 全部通过 |
| 前端API客户端 | test_client.py | 16 | ✅ 全部通过 |
| 前端GUI组件 | test_gui.py | 14 | ✅ 全部通过 |
| **总计** | **4个文件** | **51个** | **✅ 100%通过** |

## 运行方式

### 后端服务

```bash
cd backend
python3 main.py
# 服务运行在 http://localhost:5002
```

### 前端应用

```bash
cd frontend
python3 main.py
# 启动GUI界面，连接后端API
```

### Mock模式（打桩接口）

```bash
cd frontend
python3 main.py --mock
# 使用Mock模式，不依赖后端服务
```

### 测试执行

```bash
# 后端测试
cd backend/tests
python3 -m pytest test_core.py -v
python3 -m pytest test_api.py -v
python3 -m pytest -v  # 运行所有后端测试

# 前端测试
cd frontend/tests
python3 -m pytest test_client.py -v
python3 -m pytest test_gui.py -v
python3 -m pytest -v  # 运行所有前端测试
```

**注意**：如果系统中没有安装pytest，请先安装：
```bash
pip3 install pytest
```

## GUI实现细节

### GUI组件架构

```
NetworkGUI (frontend/gui/main.py)
├── setup()                    # 初始化GUI布局
│   ├── 创建主绘图区域
│   ├── 创建控制面板
│   ├── 创建信息面板
│   ├── 创建交互按钮
│   └── 注册事件处理器
│
├── draw()                     # 绘制网络拓扑
│   ├── 绘制节点
│   ├── 绘制链路
│   ├── 绘制标签
│   ├── 绘制图例
│   └── 更新信息面板
│
├── _refresh_topology()        # 刷新拓扑数据
│   ├── 调用API获取数据
│   └── 更新布局位置
│
├── _on_click()               # 处理点击事件
│   ├── 识别点击的节点
│   ├── 识别点击的链路
│   └── 更新选中状态
│
└── _handle_button()          # 处理按钮事件
    ├── 切换链路状态
    ├── 节点故障/恢复
    ├── 重置拓扑
    └── 执行测试场景
```

### GUI显示修复

**问题**：GUI窗口打开但无内容显示

**原因**：`run()` 方法中调用 `_refresh_topology()` 后未调用 `draw()` 绘制图形

**修复**：在 `run()` 方法中添加 `self.draw()` 调用

```python
def run(self):
    print("=" * 60)
    print("基于LACP与BPDU协同探测的动态自愈无环网络 - GUI模式")
    print("=" * 60)
    print("\n正在初始化GUI...")
    self.setup()
    print("正在连接后端API...")
    self._refresh_topology()
    print("正在绘制图形...")
    self.draw()  # 关键修复：绘制图形
    print("\nGUI界面已启动！")
    print("=" * 60)
    plt.show()
```

## 测试警告说明

运行测试时可能会遇到以下警告，但不影响功能：

### 1. urllib3 SSL版本警告

```
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+
```

- **原因**：macOS系统使用LibreSSL而非OpenSSL
- **影响**：⚠️ 不影响功能
- **解决方案**：可忽略或升级OpenSSL

### 2. 中文字体缺失警告

```
UserWarning: Glyph ... missing from font(s) DejaVu Sans Mono
```

- **原因**：matplotlib默认字体不支持中文
- **影响**：⚠️ 不影响功能，已配置字体支持
- **解决方案**：已在 `frontend/gui/main.py` 中配置中文字体：
  ```python
  plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
  plt.rcParams['axes.unicode_minus'] = False
  ```

### 3. Tkinter弃用警告

```
DEPRECATION WARNING: The system version of Tk is deprecated
```

- **原因**：macOS系统Tkinter版本较旧
- **影响**：⚠️ 不影响功能
- **解决方案**：设置环境变量 `export TK_SILENCE_DEPRECATION=1`

## 调试工具

### GUI调试工具（debug_gui.py）

用于诊断GUI显示问题的调试脚本，包括：
- matplotlib backend检查
- API连接测试
- 拓扑数据获取测试
- 网络图绘制测试

### GUI离线测试（test_gui_offline.py）

用于离线测试GUI功能的脚本，包括：
- GUI实例创建测试
- GUI初始化测试
- API连接测试
- 图形绘制测试
- 图形保存测试

## 技术栈

### 后端
- Python 3.9+
- Flask 3.1.2+
- networkx 2.8.0+

### 前端
- Python 3.9+
- matplotlib 3.5.0+
- networkx 2.8.0+
- Tkinter (TkAgg backend)

### 测试
- pytest 8.4.2+
- Flask test client

## 开发指南

### 添加新的API接口

1. 在 `backend/api/app.py` 中添加路由
2. 实现业务逻辑
3. 在 `frontend/gui/client.py` 中添加客户端方法
4. 在 `backend/tests/test_api.py` 中添加测试用例

### 添加新的测试场景

1. 在 `backend/api/app.py` 的 `run_scenario` 中添加场景逻辑
2. 在 `frontend/gui/client.py` 中添加场景调用方法
3. 在 `frontend/tests/test_client.py` 中添加测试用例

### 添加新的GUI组件

1. 在 `frontend/gui/main.py` 中实现组件
2. 在 `frontend/tests/test_gui.py` 中添加测试用例

## 版本信息

- Python版本：3.9+
- Flask版本：3.1.2+
- pytest版本：8.4.2+
- matplotlib版本：3.5.0+
- networkx版本：2.8.0+
