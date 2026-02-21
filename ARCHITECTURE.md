# 浏览器前端架构设计

## 项目结构

```
solo_cpc/
├── backend/                    # 后端服务
│   ├── core/                 # 核心业务逻辑
│   │   ├── node.py           # 节点类（增量ID: node_1, node_2...）
│   │   ├── link.py           # 链路类
│   │   ├── topology.py       # 拓扑管理（含连通性检测）
│   │   ├── stp.py           # 生成树计算
│   │   ├── lacp.py          # LACP探测
│   │   └── bpdu.py          # BPDU协议
│   ├── api/                  # API接口层
│   │   └── app.py           # Flask应用（含CORS支持）
│   ├── utils/                # 工具模块
│   │   └── logger.py        # 日志记录
│   ├── tests/                # 后端测试
│   │   ├── test_core.py      # 核心逻辑测试
│   │   └── test_api.py       # API接口测试
│   └── main.py              # 后端启动入口
│
├── frontend/                 # 前端应用
│   └── web/                 # 浏览器前端
│       ├── index.html       # 主页面（2x2网格布局）
│       ├── style.css        # 样式表
│       ├── app.js           # 应用逻辑（Canvas渲染）
│       └── server.py        # 静态文件服务器（可选）
│
├── requirements.txt           # 依赖包
├── README.md               # 项目说明
└── ARCHITECTURE.md         # 本文件
```

## 架构设计

### 1. 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Browser)                        │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐  │
│  │   Presentation Layer (HTML5 + CSS3)                   │  │
│  │   - 2x2 Grid Layout                                   │  │
│  │   - Control Panel (Link/Node/System)                  │  │
│  │   - Demo Panel (Auto Demo)                            │  │
│  │   - Legend & Connectivity Status                      │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼────────────────────────────────┐  │
│  │   Visualization Layer (HTML5 Canvas)                  │  │
│  │   - Network Topology Rendering                        │  │
│  │   - Node/Link State Visualization                     │  │
│  │   - Connectivity Indicators (✓/✗)                     │  │
│  │   - Selection Highlight                               │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼────────────────────────────────┐  │
│  │   Application Logic (JavaScript)                      │  │
│  │   - API Communication (fetch)                         │  │
│  │   - Event Handling                                    │  │
│  │   - Animation Loop (requestAnimationFrame)            │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         │ HTTP/JSON (CORS)                   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Backend (Flask REST API)                  │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐  │
│  │   API Layer (Flask + CORS)                            │  │
│  │   - REST Endpoints                                    │  │
│  │   - JSON Serialization                                │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼────────────────────────────────┐  │
│  │   Core Business Logic                                 │  │
│  │   - Node Management (Incremental ID: node_1, node_2)  │  │
│  │   - Link Management                                   │  │
│  │   - Topology Control                                  │  │
│  │   - STP Calculation (Spanning Tree Protocol)          │  │
│  │   - LACP Detection                                    │  │
│  │   - BPDU Protocol                                     │  │
│  │   - Connectivity Detection (BFS-based)                │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼────────────────────────────────┐  │
│  │   Test Suite                                          │  │
│  │   - Unit Tests (test_core.py)                         │  │
│  │   - Integration Tests (test_api.py)                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2. 后端架构

```
┌─────────────────────────────────────────┐
│         Backend Service              │
├─────────────────────────────────────────┤
│                                   │
│  ┌─────────────────────────────┐    │
│  │   API Layer (Flask)      │    │
│  │   - REST API             │    │
│  │   - JSON Response         │    │
│  │   - CORS Support         │    │
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
│  │   - Connectivity Detection  │    │
│  └────────────────────────────┘    │
│                                   │
│  ┌─────────────────────────────┐    │
│  │   Test Suite              │    │
│  │   - Unit Tests           │    │
│  │   - Integration Tests     │    │
│  └────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### 3. 前端架构

```
┌─────────────────────────────────────────┐
│         Frontend Application         │
├─────────────────────────────────────────┤
│                                   │
│  ┌─────────────────────────────┐    │
│  │   Presentation Layer       │    │
│  │   - HTML5 Structure        │    │
│  │   - CSS3 Styling          │    │
│  │   - 2x2 Grid Layout       │    │
│  │   - Responsive Design     │    │
│  └──────────┬──────────────────┘    │
│             │                         │
│  ┌──────────▼──────────────────┐    │
│  │   Canvas Layer            │    │
│  │   - Network Rendering      │    │
│  │   - Node/Link Drawing     │    │
│  │   - Connectivity Indicators │    │
│  │   - Animation Loop        │    │
│  └──────────┬──────────────────┘    │
│             │                         │
│  ┌──────────▼──────────────────┐    │
│  │   Logic Layer             │    │
│  │   - API Communication      │    │
│  │   - Event Handling        │    │
│  │   - State Management      │    │
│  │   - Auto Demo             │    │
│  └────────────────────────────┘    │
└─────────────────────────────────────────┘
```

## API接口设计

### 拓扑管理接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/topology | 获取完整拓扑（含连通性信息） |
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

### 调试接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/debug/status | 获取系统调试状态 |
| GET | /api/debug/nodes/{node_id} | 获取节点详细信息 |
| GET | /api/debug/links/{link_id} | 获取链路详细信息 |
| GET | /api/debug/logs | 获取最近日志内容 |

### 连通性检测API

拓扑数据中包含连通性信息，通过 `GET /api/topology` 返回的数据结构：

```json
{
  "nodes": {
    "node_1": {
      "node_id": "node_1",
      "node_name": "Node1",
      "state": "ACTIVE",
      "is_root": true,
      "connectivity": {
        "reachable": true,
        "path": [],
        "blocked_by": null,
        "is_root": true
      }
    },
    "node_2": {
      "connectivity": {
        "reachable": true,
        "path": [...],
        "blocked_by": null
      }
    }
  },
  "connectivity_summary": {
    "total_nodes": 4,
    "reachable_nodes": 3,
    "unreachable_nodes": 1
  }
}
```

## 连通性检测机制

### 检测算法

采用**广度优先搜索（BFS）**算法检测各节点到根节点的连通性：

```
check_connectivity_to_root(node):
    1. 检查根节点是否存在
    2. 检查目标节点是否为根节点
    3. 检查目标节点是否已失败
    4. BFS遍历寻找到根节点的路径
       - 只遍历活跃节点
       - 只遍历UP状态的链路
    5. 返回结果：
       - reachable: 是否可达
       - path: 路径信息
       - blocked_by: 阻塞原因
```

### 阻塞原因类型

| 原因 | 说明 |
|------|------|
| no_root | 网络中没有根节点 |
| node_failed | 目标节点已失败 |
| no_path | 无法找到到根节点的路径 |

### 可视化展示

- **节点上方指示器**：
  - 绿色圆圈 + ✓：可达根节点
  - 红色圆圈 + ✗：不可达根节点
- **右侧状态面板**：显示所有节点的详细连通状态

## 测试策略

### 后端测试

1. **单元测试**：测试核心业务逻辑（test_core.py）
   - Node类测试
   - Link类测试
   - Topology类测试

2. **集成测试**：测试API接口（test_api.py）
   - 拓扑管理API
   - 节点操作API
   - 链路操作API
   - 测试场景API

### 测试执行

```bash
# 后端测试
cd backend/tests
python3 -m pytest test_core.py -v
python3 -m pytest test_api.py -v
python3 -m pytest -v  # 运行所有后端测试
```

**注意**：如果系统中没有安装pytest，请先安装：
```bash
pip3 install pytest
```

### 测试警告说明

运行测试时可能会遇到以下警告，但不影响功能：

#### urllib3 SSL版本警告

```
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+
```

- **原因**：macOS系统使用LibreSSL而非OpenSSL
- **影响**：⚠️ 不影响功能
- **解决方案**：可忽略或升级OpenSSL

## 运行方式

### 后端服务

```bash
cd backend
python3 main.py
# 服务运行在 http://localhost:5002
```

### 前端应用

#### 方式一：直接打开HTML文件

在浏览器中直接打开 `frontend/web/index.html` 文件。

#### 方式二：使用Python简易服务器

```bash
cd frontend/web
python3 -m http.server 8080
# 访问 http://localhost:8080
```

#### 方式三：使用Flask静态文件服务器

```bash
cd frontend/web
python3 server.py
# 访问 http://localhost:8080
```

## 前端实现细节

### 页面布局（2x2网格）

```
┌─────────────────────────────┬─────────────────────────────┐
│                             │           Legend            │
│      Network Canvas         │     (Nodes & Links)         │
│    (HTML5 Canvas)           ├─────────────────────────────┤
│                             │     Connectivity Status     │
│                             ├─────────────────────────────┤
├─────────────────────────────┤     Information Panel       │
│    Control Buttons          ├─────────────────────────────┤
│  (Link/Node/System/Demo)    │       Demo Status           │
└─────────────────────────────┴─────────────────────────────┘
```

### Canvas渲染架构

```javascript
// 主要函数结构
app.js
├── resizeCanvas()              // 调整Canvas尺寸
├── fetchTopology()             // 获取拓扑数据
├── calculateNodePositions()    // 计算节点位置
├── draw()                      // 主绘制函数
│   ├── drawLinks()            // 绘制链路
│   ├── drawNodes()            // 绘制节点
│   └── drawConnectivityIndicators() // 绘制连通性指示器
├── startAnimationLoop()        // 动画循环
├── updateConnectivityPanel()   // 更新连通性面板
├── updateInfoPanel()           // 更新信息面板
└── 事件处理器
    ├── canvas click           // 点击选择
    └── button clicks          // 按钮操作
```

### 交互式操作

- **点击选择**：点击节点或链路进行选择（黄色高亮）
- **控制按钮**：
  - **Link Control**: DN (Down), UP (Up), TG (Toggle)
  - **Node Control**: FL (Fail), RC (Recover)
  - **System**: RST (Reset)
  - **Auto Demo**: DEMO (自动演示)

### 自动演示场景

点击 **DEMO** 按钮启动自动演示：

1. **Step 1**: 初始状态 - 所有节点和链路正常
2. **Step 2**: 链路故障 - Node1-Node2链路DOWN
3. **Step 3**: 节点故障 - Node3失败
4. **Step 4**: 观察网络状态 - 剩余节点保持连通
5. **Step 5**: 恢复Node3
6. **Step 6**: 恢复Node1-Node2链路
7. **Step 7**: 最终状态 - 网络恢复最优状态

## 调试工具

### 调试API接口

通过RESTful API实现调试查询，可在浏览器中直接访问：

#### 1. 系统调试状态

```
GET http://localhost:5002/api/debug/status
```

返回示例：
```json
{
  "topology": {
    "total_nodes": 4,
    "active_nodes": 4,
    "failed_nodes": 0,
    "total_links": 6,
    "up_links": 6,
    "down_links": 0,
    "spanning_tree_links": 3
  },
  "root_node": {
    "node_id": "node_1",
    "node_name": "Node1"
  },
  "stp": { ... },
  "timestamp": 1708123456.789
}
```

#### 2. 节点详细信息

```
GET http://localhost:5002/api/debug/nodes/node_1
```

返回示例：
```json
{
  "node": {
    "node_id": "node_1",
    "node_name": "Node1",
    "state": "ACTIVE",
    "is_root": true
  },
  "ports": {
    "1": {"port_id": 1, "state": "FORWARDING", "node_id": "node_1"},
    "2": {"port_id": 2, "state": "FORWARDING", "node_id": "node_1"},
    "3": {"port_id": 3, "state": "BLOCKING", "node_id": "node_1"}
  },
  "connected_links": [
    {
      "link_id": "node_1-1<->node_2-1",
      "state": "UP",
      "connected_to": "Node2",
      "bandwidth": 1000,
      "latency": 1,
      "is_in_spanning_tree": true
    }
  ],
  "is_root": true,
  "root_path_cost": 0,
  "parent_port": null
}
```

#### 3. 链路详细信息

```
GET http://localhost:5002/api/debug/links/node_1-1<->node_2-1
```

返回示例：
```json
{
  "link": {
    "link_id": "node_1-1<->node_2-1",
    "state": "UP",
    "bandwidth": 1000,
    "latency": 1
  },
  "endpoints": {
    "node1": {
      "node_id": "node_1",
      "node_name": "Node1",
      "port_id": 1
    },
    "node2": {
      "node_id": "node_2",
      "node_name": "Node2",
      "port_id": 1
    }
  },
  "lacp": {
    "success_count": 10,
    "fail_count": 0,
    "last_lacp_time": 1708123456.789
  },
  "is_in_spanning_tree": true,
  "created_at": 1708123400.123
}
```

#### 4. 日志查询

```
GET http://localhost:5002/api/debug/logs
```

返回示例：
```json
{
  "log_directory": "/path/to/logs",
  "logs": [
    {
      "filename": "network_20260218.log",
      "size": 10240,
      "last_100_lines": [
        "2026-02-18 10:39:32 | INFO | Startup: NetworkAPI",
        "2026-02-18 10:39:32 | INFO | API Request: GET /api/topology",
        ...
      ]
    }
  ]
}
```

## 技术栈

### 后端
- Python 3.9+
- Flask 3.1.2+
- Flask-CORS（跨域支持）

### 前端
- HTML5
- CSS3
- JavaScript (ES6+)
- HTML5 Canvas API

### 测试
- pytest 8.4.2+
- Flask test client

## 开发指南

### 添加新的API接口

1. 在 `backend/api/app.py` 中添加路由
2. 实现业务逻辑
3. 在 `backend/tests/test_api.py` 中添加测试用例

### 添加新的测试场景

1. 在 `backend/api/app.py` 的 `run_scenario` 中添加场景逻辑
2. 在 `frontend/web/app.js` 中添加场景调用方法

### 修改前端布局

1. 编辑 `frontend/web/index.html` 修改页面结构
2. 编辑 `frontend/web/style.css` 修改样式
3. 编辑 `frontend/web/app.js` 修改交互逻辑

## 版本信息

- Python版本：3.9+
- Flask版本：3.1.2+
- pytest版本：8.4.2+

## 更新日志

### v2.0.0 (最新)
- ✅ 重构为浏览器前端架构
- ✅ 使用HTML5 Canvas替代matplotlib
- ✅ 实现2x2网格布局
- ✅ 添加连通性检测功能（BFS算法）
- ✅ 添加连通性可视化指示器
- ✅ 实现自动演示场景
- ✅ 节点ID改为增量格式（node_1, node_2...）
- ✅ 移除Python GUI依赖
