# 基于LACP与BPDU协同探测的动态自愈无环网络

## 这是一个使用AI辅助实现的项目
本项目可用于帮助研究 STP 和 RSTP 协议，并基于一个真实的目标验证AI在软件开发中所占的分量

## 项目概述

本项目采用前后端分离架构，实现了基于LACP与BPDU协同探测的动态自愈无环网络仿真系统。后端提供REST API接口，前端采用浏览器技术栈（HTML5 Canvas + JavaScript）实现网络拓扑可视化。

## 架构设计

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
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 项目结构

```
tinyrstp/
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
│       └── server.py        # 静态文件服务器（推荐使用）
│
├── requirements.txt           # 依赖包
├── ARCHITECTURE.md          # 架构设计文档
└── README.md               # 本文件
```

## 安装依赖

```bash
pip3 install -r requirements.txt
```

**注意**：如果系统中没有安装pytest，请先安装：
```bash
pip3 install pytest
```

## 运行方式

### 重要提示

确保先进入项目根目录（包含 README.md 和 requirements.txt 的目录）：

```bash
cd /path/to/tinyrstp/tinyrstp
```

### 后端服务

```bash
cd backend
python3 main.py
```

后端服务将运行在：**http://localhost:5002**

### 前端应用

#### 推荐方式：使用项目自带的CORS服务器

```bash
cd frontend/web
python3 server.py
```

然后在浏览器中访问：**http://localhost:8080**

此方式支持CORS，推荐使用。

#### 方式二：使用Python简易服务器

```bash
cd frontend/web
python3 -m http.server 8080
```

然后在浏览器中访问：**http://localhost:8080**

#### 方式三：直接打开HTML文件

在浏览器中直接打开 `frontend/web/index.html` 文件。

**注意**：直接打开HTML文件可能会遇到CORS跨域问题，建议使用前两种方式。

### 完整启动流程

1. **启动后端服务**（终端1）：
   ```bash
   cd /path/to/tinyrstp/tinyrstp/backend
   python3 main.py
   ```

2. **启动前端服务**（终端2）：
   ```bash
   cd /path/to/tinyrstp/tinyrstp/frontend/web
   python3 server.py
   ```

3. **访问应用**：
   在浏览器中打开：**http://localhost:8080**

## API接口

### 拓扑管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/topology | 获取完整拓扑（含连通性信息） |
| POST | /api/topology/reset | 重置拓扑 |
| GET | /api/topology/nodes | 获取所有节点 |
| GET | /api/topology/links | 获取所有链路 |
| GET | /api/topology/spanning-tree | 获取生成树 |

### 节点操作

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/nodes/{node_id}/fail | 注入节点故障 |
| POST | /api/nodes/{node_id}/recover | 恢复节点 |

### 链路操作

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/links/{link_id}/toggle | 切换链路状态 |
| POST | /api/links/{link_id}/up | 链路UP |
| POST | /api/links/{link_id}/down | 链路DOWN |

### 测试场景

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

**调试接口使用示例**（在浏览器中访问）：

```
# 查看系统状态
http://localhost:5002/api/debug/status

# 查看节点详情（node_id需要替换为实际ID）
http://localhost:5002/api/debug/nodes/node_1

# 查看链路详情（link_id需要替换为实际ID）
http://localhost:5002/api/debug/links/node_1-1<->node_2-1

# 查看日志
http://localhost:5002/api/debug/logs
```

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

## 测试

### 后端测试

```bash
cd backend/tests
python3 -m pytest test_core.py -v
python3 -m pytest test_api.py -v
python3 -m pytest -v  # 运行所有后端测试
```

**测试覆盖**：
- test_core.py：核心业务逻辑测试
- test_api.py：API接口测试

### 测试警告说明

运行测试时可能会遇到以下警告，但不影响功能：

#### 1. urllib3 SSL版本警告
```
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+
```
- **原因**：macOS系统使用LibreSSL而非OpenSSL
- **影响**：⚠️ 不影响功能
- **解决方案**：可忽略或升级OpenSSL

## 前端功能

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

### 交互式操作

- **点击选择**：点击节点或链路进行选择（黄色高亮）
- **控制按钮**：
  - **Link Control**: DN (Down), UP (Up), TG (Toggle)
  - **Node Control**: FL (Fail), RC (Recover)
  - **System**: RST (Reset)
  - **Auto Demo**: DEMO (自动演示)

### 连通性可视化

- **✓ 绿色圆圈**：节点可达根节点
- **✗ 红色圆圈**：节点不可达根节点
- **状态面板**：右侧显示所有节点的连通状态

### 自动演示场景

点击 **DEMO** 按钮启动自动演示：

1. **Step 1**: 初始状态 - 所有节点和链路正常
2. **Step 2**: 链路故障 - Node1-Node2链路DOWN
3. **Step 3**: 节点故障 - Node3失败
4. **Step 4**: 观察网络状态 - 剩余节点保持连通
5. **Step 5**: 恢复Node3
6. **Step 6**: 恢复Node1-Node2链路
7. **Step 7**: 最终状态 - 网络恢复最优状态

### 前端显示说明

**重要**：前端需要后端服务运行才能正常工作。启动时会看到以下输出：

```
后端服务运行在: http://localhost:5002
前端访问地址: http://localhost:8080 (或直接打开index.html)
```

如果前端无法显示拓扑数据，请检查：
1. 后端服务是否正常运行（http://localhost:5002）
2. 浏览器控制台是否有CORS错误
3. 网络连接是否正常

## 核心特性

- ✅ 前后端分离架构
- ✅ 浏览器前端（HTML5 Canvas + JavaScript）
- ✅ REST API接口（Flask + CORS）
- ✅ 实时拓扑可视化
- ✅ 连通性检测（BFS算法）
- ✅ 连通性可视化指示器（✓/✗）
- ✅ 故障注入/恢复
- ✅ 动态生成树计算（STP）
- ✅ LACP/BPDU协同探测
- ✅ 自动演示场景

## 连通性检测机制

### 检测算法

采用**广度优先搜索（BFS）**算法检测各节点到根节点的连通性：

1. **根节点选举**：选择活跃节点中ID最小的节点作为根节点
2. **BFS遍历**：从目标节点出发，沿活跃链路遍历寻找根节点
3. **状态判断**：
   - `reachable: true` - 存在到根节点的路径
   - `reachable: false` - 无法到达根节点
   - `blocked_by` - 记录阻塞原因（node_failed/no_root/no_path）

### 可视化展示

- **节点上方指示器**：
  - 绿色圆圈 + ✓：可达
  - 红色圆圈 + ✗：不可达
- **右侧状态面板**：显示所有节点的详细连通状态

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

## 测试统计

| 模块 | 测试文件 | 状态 |
|------|---------|------|
| 后端核心逻辑 | test_core.py | ✅ 全部通过 |
| 后端API接口 | test_api.py | ✅ 全部通过 |

## 常见问题

### Q1: 后端服务启动失败，提示端口被占用

**A**: 端口5002被占用，可以修改 `backend/main.py` 中的端口号，或停止占用该端口的进程：
```bash
lsof -ti :5002 | xargs kill -9
```

### Q2: 前端无法连接后端

**A**: 确保后端服务已启动，并且运行在正确的端口（默认5002）。检查浏览器控制台是否有CORS错误。

### Q3: Canvas不显示节点

**A**: 确保后端服务正常运行，检查浏览器控制台的网络请求是否成功。如果Canvas尺寸为0，页面加载后会自动重试。

### Q4: 连通性显示不正确

**A**: 连通性检测基于当前生成树状态。确保：
1. 根节点已正确选举
2. 生成树已计算
3. 后端服务已重启以加载最新代码

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

### v1.2.1
- ✅ 将GUI界面中的所有中文替换为英文
- ✅ 修复字体警告问题
- ✅ 更新相关文档

### v1.2.0
- ✅ 添加调试API接口（/api/debug/*）
- ✅ 支持通过浏览器查询节点/链路状态
- ✅ 支持通过API查看日志内容
- ✅ 修复matplotlib后端兼容性问题
- ✅ 自动检测最佳GUI后端
- ✅ 修复GUI窗口打开但无内容显示的问题
- ✅ 添加GUI调试工具（debug_gui.py）
- ✅ 添加GUI离线测试（test_gui_offline.py）
- ✅ 更新测试命令为 `python3 -m pytest`
- ✅ 完善测试覆盖（51个测试用例）
- ✅ 更新架构文档和README

### v1.0.0
- ✅ 实现前后端分离架构
- ✅ 实现REST API接口
- ✅ 实现打桩接口支持
- ✅ 实现交互式GUI
- ✅ 实现自动化测试用例
