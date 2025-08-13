# GUI与核心工作流接口说明

## 概述

本文档描述了GUI界面与项目核心工作流之间的接口设计和使用方法。

## 架构设计

### 1. 接口层次结构

```
GUI Layer
├── components/
│   ├── workflow_panel.py      # 工作流管理面板
│   ├── data_browser.py        # 数据浏览器
│   └── llm_interface.py       # LLM测试界面
├── services/
│   └── workflow_service.py    # 工作流服务接口
└── app.py                     # 主应用入口

Core Workflow Layer
├── Workflow_Entry.py          # 工作流入口
├── Data/                      # 数据模型
├── Entities/                  # LLM实体
├── Tools/                     # 工具集
└── Interfaces/                # API接口
```

### 2. 核心组件

#### WorkflowService
- **功能**: 管理GUI与核心工作流的交互
- **主要方法**:
  - `create_session(user_requirements)`: 创建新会话
  - `start_workflow(session_id, supplementary_info)`: 启动工作流
  - `pause_workflow(session_id)`: 暂停工作流
  - `cancel_workflow(session_id)`: 取消工作流
  - `get_session_status(session_id)`: 获取会话状态
  - `get_workflow_results(session_id)`: 获取执行结果

#### WorkflowPanel
- **功能**: 工作流管理界面
- **特性**:
  - 任务配置输入
  - 实时状态监控
  - 进度条显示
  - 结果展示
  - 会话管理

#### DataBrowser
- **功能**: 数据浏览和管理
- **特性**:
  - Redis数据库浏览
  - 历史记录查看
  - 文件导入导出
  - 数据统计分析

## 使用指南

### 1. 启动GUI界面

```bash
cd GUI
streamlit run app.py
```

### 2. 工作流操作流程

1. **创建任务**
   - 在"Agent工作流"选项卡中
   - 输入用户需求描述
   - 可选择添加补充信息
   - 点击"启动工作流"

2. **监控执行**
   - 实时查看执行状态
   - 观察进度条和阶段信息
   - 可暂停或取消工作流

3. **查看结果**
   - 工作流完成后自动显示结果
   - 查看用户画像、策略计划、子目标等
   - 浏览工作记忆数据

4. **管理会话**
   - 查看历史会话列表
   - 删除不需要的会话
   - 重新查看已完成的结果

### 3. 数据管理

1. **Redis数据浏览**
   - 连接Redis数据库
   - 搜索和查看键值对
   - 删除不需要的数据

2. **历史记录管理**
   - 浏览循环历史记录
   - 查看不同会话的执行过程
   - 分析策略和执行效果

3. **文件操作**
   - 导入JSON格式的工作流数据
   - 导出当前数据到本地文件
   - 数据格式验证和预览

## 配置说明

### 1. 环境变量

确保设置以下环境变量：
- `OPENAI_API_KEY`: OpenAI API密钥
- `OPENAI_BASE_URL`: OpenAI基础URL（可选）
- `GOOGLE_CLOUD_API_KEY`: Google Cloud API密钥（可选）
- `REDIS_HOST`: Redis主机地址
- `REDIS_PORT`: Redis端口
- `REDIS_DB`: Redis数据库编号

### 2. 依赖安装

```bash
pip install streamlit
pip install redis
pip install openai
pip install google-generativeai
pip install pydantic
```

## 注意事项

### 1. 线程安全
- WorkflowService使用线程锁确保并发安全
- 工作流在后台线程中执行，不阻塞GUI

### 2. 错误处理
- 所有API调用都有异常处理
- 错误信息会显示在界面上
- 工作流失败时状态会正确更新

### 3. 内存管理
- 会话数据存储在内存中
- 大量数据会影响性能
- 建议定期清理不需要的会话

### 4. 数据持久化
- Redis用于存储工具执行结果
- 历史记录通过CycleHistory类管理
- GUI会话数据不自动持久化

## 扩展开发

### 1. 添加新组件

```python
# 创建新组件文件
class NewComponent:
    def __init__(self):
        pass
    
    def render(self):
        st.subheader("新组件")
        # 组件逻辑

# 在app.py中集成
from components.new_component import NewComponent
```

### 2. 扩展服务接口

```python
# 在WorkflowService中添加新方法
def new_feature(self, session_id: str) -> bool:
    # 新功能实现
    pass
```

### 3. 自定义数据源

```python
# 在DataBrowser中添加新数据源
def _render_custom_source(self):
    # 自定义数据源逻辑
    pass
```

## 故障排除

### 1. 常见问题

- **Redis连接失败**: 检查Redis服务是否启动，配置是否正确
- **工作流启动失败**: 检查环境变量和API密钥
- **界面无响应**: 检查Streamlit服务状态
- **数据加载错误**: 检查数据格式和权限

### 2. 调试方法

- 查看Streamlit控制台输出
- 检查Redis中的数据
- 使用浏览器开发者工具
- 查看Python异常堆栈

## 更新日志

- **v1.0**: 初始版本，基本工作流管理功能
- **v1.1**: 添加数据浏览器和会话管理
- **v1.2**: 优化界面和错误处理