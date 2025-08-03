# 环境变量设置指南

## 1. 创建.env文件

复制 `env.example` 文件为 `.env`：

```bash
cp env.example .env
```

## 2. 编辑.env文件

在 `.env` 文件中填入你的实际API密钥：

```bash
# API Keys
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
GOOGLE_CLOUD_API_KEY=your-actual-google-cloud-api-key-here
GOOGLE_CLOUD_PROJECT_ID=your-actual-project-id-here

# 其他配置...
```

## 3. 安装依赖（可选）

如果你想使用 `python-dotenv` 库自动加载.env文件：

```bash
pip install python-dotenv
```

## 4. 在代码中使用

### 方法1：使用python-dotenv（推荐）

```python
from dotenv import load_dotenv
import os

# 加载.env文件
load_dotenv()

# 获取环境变量
api_key = os.getenv('OPENAI_API_KEY')
```

### 方法2：直接使用os.environ

```python
import os

# 直接获取环境变量
api_key = os.getenv('OPENAI_API_KEY')
```

## 5. 在LLM接口中使用

```python
from Interfaces.llm_api_interface import OpenAIInterface, GoogleCloudInterface

# 创建接口实例（会自动从环境变量获取API密钥）
openai_interface = OpenAIInterface()
google_interface = GoogleCloudInterface()
```

## 6. 安全注意事项

- `.env` 文件已经被添加到 `.gitignore` 中，不会被提交到版本控制
- 永远不要在代码中硬编码API密钥
- 在生产环境中，建议使用更安全的环境变量管理方式

## 7. 测试环境变量

运行示例脚本检查环境变量是否正确设置：

```bash
python example_usage.py
``` 