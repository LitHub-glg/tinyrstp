# 基于LACP与BPDU协同探测的动态自愈无环网络 - 前后端分离架构

## 项目概述

本项目采用前后端分离架构，实现了基于LACP与BPDU协同探测的动态自愈无环网络仿真系统。后端提供REST API接口，前端通过API客户端（支持打桩）进行交互。

## 架构设计

```
┌─────────────────────────────────────────┐
│         Frontend (GUI)             │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────┐    │
│  │   GUI Layer              │    │
│  │   - Network Visualization  │    │
│  │   - Control Panel        │    │
│  │   - Info Display        │    │
│  └──────────┬──────────────────┘    │
│             │                         │
│  ┌──────────▼──────────────────┐    │
│  │   API Client (Stub)      │    │
│  │   - REST API Client      │    │
│  │   - Mock Interface      │    │
│  │   - Test Automation     │    │
│  └──────────┬──────────────────┘    │
│             │ HTTP/JSON              │
└─────────────┼───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         Backend (REST API)            │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────┐    │
│  │   API Layer (Flask)      │    │
│  │   - REST Endpoints       │    │
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
└─────────────────────────────────────────┘
```

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
│   │   └── app.py           # Flask应用
│   ├── tests/                # 后端测试
│   │   ├── test_core.py      # 核心逻辑测试
│   │   └── test_api.py       # API接口测试
│   └── main.py              # 后端启动入口
│
├── frontend/                 # 前端应用
│   ├── gui/                 # GUI界面
│   │   ├── main.py          # 主界面
│   │   └── client.py       # API客户端（打桩接口）
│   ├── tests/                # 前端测试
│   │   ├── test_client.py   # 客户端测试
│   │   └── test_gui.py      # GUI组件测试
│   ├── debug_gui.py         # GUI调试工具
│   ├── test_gui_offline.py  # GUI离线测试
│   └── main.py              # 前端启动入口
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

### 后端服务

```bash
cd backend
python3 main.py
```

后端服务将运行在：**http://localhost:5002**

### 前端应用

#### 连接真实后端

```bash
cd frontend
python3 main.py
```

#### 使用Mock模式（打桩接口）

```bash
cd frontend
python3 main.py --mock
```

## API接口

### 拓扑管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/topology | 获取完整拓扑 |
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
http://localhost:5002/api/debug/nodes/abc12345

# 查看链路详情（link_id需要替换为实际ID）
http://localhost:5002/api/debug/links/abc12345-1<->def67890-1

# 查看日志
http://localhost:5002/api/debug/logs
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
- test_core.py：7个测试用例（核心业务逻辑）
- test_api.py：14个测试用例（API接口）
- **总计**：21个测试用例

### 前端测试

```bash
cd frontend/tests
python3 -m pytest test_client.py -v
python3 -m pytest test_gui.py -v
python3 -m pytest -v  # 运行所有前端测试
```

**测试覆盖**：
- test_client.py：16个测试用例（API客户端和自动化场景）
- test_gui.py：14个测试用例（GUI组件）
- **总计**：30个测试用例

### 测试警告说明

运行测试时可能会遇到以下警告，但不影响功能：

#### 1. urllib3 SSL版本警告
```
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+
```
- **原因**：macOS系统使用LibreSSL而非OpenSSL
- **影响**：⚠️ 不影响功能
- **解决方案**：可忽略或升级OpenSSL

#### 2. 中文字体缺失警告
```
UserWarning: Glyph ... missing from font(s) DejaVu Sans Mono
```
- **原因**：matplotlib默认字体不支持中文（现已替换为英文）
- **影响**：⚠️ 不影响功能
- **解决方案**：已将GUI界面中的所有中文替换为英文

#### 3. Tkinter弃用警告
```
DEPRECATION WARNING: The system version of Tk is deprecated
```
- **原因**：macOS系统Tkinter版本较旧
- **影响**：⚠️ 不影响功能
- **解决方案**：设置环境变量 `export TK_SILENCE_DEPRECATION=1`

## GUI功能

### 交互式操作

- **点击选择**：点击节点或链路进行选择（黄色高亮）
- **按钮操作**：
  - 切换链路状态
  - 节点故障/恢复
  - 重置拓扑
  - 场景1：链路故障
  - 场景2：链路恢复
  - 场景3：节点故障

### 自动化测试场景

1. **场景1：链路故障**
   - 注入Node1-Node2链路故障
   - 验证生成树重构
   - 确认网络连通性

2. **场景2：链路恢复**
   - 恢复Node1-Node2链路
   - 验证生成树优化
   - 确认网络恢复

3. **场景3：节点故障**
   - 注入Node3节点故障
   - 验证生成树重构
   - 确认剩余节点连通

### GUI显示说明

**重要**：GUI界面需要正确初始化才能显示内容。启动时会看到以下输出：

```
============================================================
基于LACP与BPDU协同探测的动态自愈无环网络 - GUI模式
============================================================

正在初始化GUI...
正在连接后端API...
正在绘制图形...

GUI界面已启动！
============================================================
```

如果GUI窗口打开但无内容显示，请检查：
1. 后端服务是否正常运行（http://localhost:5002）
2. 网络连接是否正常
3. 查看终端输出是否有错误信息

## 打桩接口（Mock）

前端API客户端支持Mock模式，用于：

1. **前端独立测试**：不依赖后端服务
2. **自动化测试**：通过打桩接口执行测试用例
3. **开发调试**：快速验证前端逻辑

### 启用Mock模式

```python
from frontend.gui.client import APIClient

client = APIClient()
client.enable_mock()  # 启用打桩
```

### Mock数据结构

```python
client.mock_data = {
    'topology': {
        'nodes': {},
        'links': {},
        'spanning_tree': [],
        'root_node': None
    },
    'spanning_tree': {
        'root_node': None,
        'link_count': 0,
        'node_count': 0,
        'links': []
    }
}
```

## 调试工具

### GUI调试工具

```bash
cd frontend
python3 debug_gui.py
```

用于诊断GUI显示问题的调试脚本，包括：
- matplotlib backend检查
- API连接测试
- 拓扑数据获取测试
- 网络图绘制测试

### GUI离线测试

```bash
cd frontend
python3 test_gui_offline.py
```

用于离线测试GUI功能的脚本，包括：
- GUI实例创建测试
- GUI初始化测试
- API连接测试
- 图形绘制测试
- 图形保存测试

## 核心特性

- ✅ 前后端分离架构
- ✅ REST API接口
- ✅ 打桩接口支持
- ✅ 完整的测试覆盖（51个测试用例）
- ✅ 交互式GUI
- ✅ 实时拓扑可视化
- ✅ 故障注入/恢复
- ✅ 动态生成树计算
- ✅ LACP/BPDU协同探测

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

## 测试统计

| 模块 | 测试文件 | 测试用例数 | 状态 |
|------|---------|----------|------|
| 后端核心逻辑 | test_core.py | 7 | ✅ 全部通过 |
| 后端API接口 | test_api.py | 14 | ✅ 全部通过 |
| 前端API客户端 | test_client.py | 16 | ✅ 全部通过 |
| 前端GUI组件 | test_gui.py | 14 | ✅ 全部通过 |
| **总计** | **4个文件** | **51个** | **✅ 100%通过** |

## 常见问题

### Q1: 后端服务启动失败，提示端口被占用

**A**: 端口5002被占用，可以修改 `backend/main.py` 中的端口号，或停止占用该端口的进程。

### Q2: 前端无法连接后端

**A**: 确保后端服务已启动，并且运行在正确的端口（默认5002）。检查防火墙设置。

### Q3: GUI窗口打开但无内容显示

**A**: 这是已修复的问题。确保使用最新版本的代码。如果仍有问题：
1. 检查后端服务是否正常运行
2. 查看终端输出是否有错误信息
3. 运行 `python3 debug_gui.py` 进行诊断

### Q4: 测试运行时出现大量警告

**A**: 这些警告不影响功能，可以忽略。如需清理输出，可以在测试代码中添加警告过滤。

### Q5: GUI界面中文显示为方框

**A**: 已在 `frontend/gui/main.py` 中配置中文字体。如仍有问题，请确保系统安装了中文字体。

## 版本信息

- Python版本：3.9+
- Flask版本：3.1.2+
- pytest版本：8.4.2+
- matplotlib版本：3.5.0+
- networkx版本：2.8.0+

## 更新日志

### v1.2.1 (最新)
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
