# 项目架构开发文档

本文档概述了项目中所有核心类的结构，包括它们的继承关系和方法，以便于开发人员快速理解代码架构并进行协作。

---

### `Data/mcp_models.py`
*   `class ExecutionLogEntry(pydantic.BaseModel)`: 用于记录执行历史中的单个条目。
*   `class MCP(pydantic.BaseModel)`: 贯穿任务全程的核心数据对象（任务简报）。
    *   `class Config`: Pydantic 内部配置类。

---

### `Interfaces/llm_api_interface.py`
*   `class LLMAPIInterface(abc.ABC)`: LLM API 的抽象基类。
    *   `@abstractmethod def get_completion(self, prompt, model, **kwargs)`: 获取 LLM 文本补全的抽象方法。
*   `class OpenAIInterface(LLMAPIInterface)`: `LLMAPIInterface` 的 OpenAI 实现。
    *   `def get_completion(self, prompt, model, **kwargs)`: 具体的 OpenAI API 调用。
*   `class GoogleCloudInterface(LLMAPIInterface)`: `LLMAPIInterface` 的 Google Cloud 实现。
    *   `def get_completion(self, prompt, model, **kwargs)`: 具体的 Google Cloud API 调用。

---

### `Interfaces/database_interface.py`
*   `class DatabaseInterface(abc.ABC)`: 数据库交互的抽象基类。
    *   `@abstractmethod def connect(self)`: 建立连接。
    *   `@abstractmethod def disconnect(self)`: 断开连接。
    *   `@abstractmethod def store_data(self, key, data)`: 存储数据。
    *   `@abstractmethod def retrieve_data(self, key)`: 检索数据。
*   `class RedisJSONInterface(DatabaseInterface)`: `DatabaseInterface` 的 RedisJSON 实现。
    *   `def connect(self)`: 连接到 Redis。
    *   `def disconnect(self)`: 从 Redis 断开。
    *   `def store_data(self, key, data)`: 将数据存入 RedisJSON。
    *   `def retrieve_data(self, key)`: 从 RedisJSON 检索数据。

---

### `Entities/llm_entities.py`
*   `class BaseLLMEntity(abc.ABC)`: 所有 LLM 实体的基类。
    *   `def __init__(self, llm_interface)`: 初始化方法。
    *   `@abstractmethod def process(self, mcp)`: 处理 MCP 对象的抽象方法。
*   `class LLMStrategyPlanner(BaseLLMEntity)`: 战略规划器。
    *   `def process(self, mcp)`: 生成宏观战略计划。
*   `class LLMTaskPlanner(BaseLLMEntity)`: 任务规划器。
    *   `def process(self, mcp)`: 生成具体的子目标和命令。
*   `class LLMFilterSummary(BaseLLMEntity)`: 筛选与摘要器。
    *   `def process_data(self, raw_data)`: 将原始数据处理为摘要。

---

### `Entities/verification_entities.py`
*   `class BaseVerificationEntity(abc.ABC)`: 所有验证实体的基类。
    *   `@abstractmethod def verify(self, mcp)`: 执行验证的抽象方法。
*   `class PredictionVerification(BaseVerificationEntity)`: 战术层面的预测验证器。
    *   `def verify(self, mcp)`: 验证上一步执行结果是否符合预期。
*   `class RequirementsVerification(BaseVerificationEntity)`: 战略层面的需求验证器。
    *   `def verify(self, mcp)`: 验证最终结果是否满足用户初始需求。

---

### `Tools/available_tools.py`
*   `class BaseTool(abc.ABC)`: 所有工具的抽象基类。
    *   `@abstractmethod def execute(self, **kwargs)`: 执行工具逻辑的抽象方法。
*   `class WebSearchTool(BaseTool)`: 网页搜索工具。
    *   `def execute(self, query, **kwargs)`: 执行搜索。
*   `class StructuredDataAPITool(BaseTool)`: 结构化数据 API 工具。
    *   `def execute(self, endpoint, params, **kwargs)`: 调用 API。
*   `class ToolRegistry`: 用于管理和查找所有可用工具。
    *   `def __init__(self)`: 初始化并注册所有工具。
    *   `def get_tool(self, name)`: 根据名称获取工具实例。
    *   `def list_tools(self)`: 返回所有可用工具的名称。

---

### `Tools/executor.py`
*   `class Executor`: 执行器，负责调用工具和协调数据流。
    *   `def __init__(self, db_interface, summarizer)`: 初始化执行器。
    *   `def execute_command(self, mcp)`: 执行 MCP 中定义的命令。

