# load_dotenv 使用指南

## 什么是 load_dotenv？

`load_dotenv()` 是 `python-dotenv` 库的核心函数，用于从 `.env` 文件中加载环境变量到 `os.environ` 中。

## 安装

```bash
pip install python-dotenv
```

## 基本用法

### 1. 最简单的用法

```python
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

# 获取环境变量
api_key = os.getenv('OPENAI_API_KEY')
```

### 2. 指定 .env 文件路径

```python
from dotenv import load_dotenv
import os

# 指定 .env 文件路径
load_dotenv('.env')                    # 当前目录
load_dotenv('../.env')                 # 上级目录
load_dotenv('/absolute/path/.env')     # 绝对路径
```

### 3. 检查文件是否存在

```python
from dotenv import load_dotenv
import os

# 检查 .env 文件是否存在
if os.path.exists('.env'):
    load_dotenv()
    print("成功加载 .env 文件")
else:
    print("警告：.env 文件不存在")
```

### 4. 设置默认值

```python
from dotenv import load_dotenv
import os

load_dotenv()

# 设置默认值
api_key = os.getenv('OPENAI_API_KEY', 'default_key')
model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
max_tokens = int(os.getenv('MAX_TOKENS', '300'))
temperature = float(os.getenv('TEMPERATURE', '0.7'))
```

## 在你的项目中使用

### 在 web_search.py 中的使用示例

```python
# 在文件开头添加
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

class SearchEngine:
    def __init__(self, keywords, num_results=5):
        self.keywords = keywords
        self.num_results = num_results
        
        # 从环境变量获取配置
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '300'))
        
        # 检查必要的环境变量
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 环境变量未设置")
        
        # ... 其他初始化代码
```

## .env 文件格式

```bash
# API Keys
OPENAI_API_KEY=sk-your-actual-api-key-here
GOOGLE_CLOUD_API_KEY=your-google-api-key-here

# 配置选项
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=300
TEMPERATURE=0.7

# 数据库配置
REDIS_HOST=localhost
REDIS_PORT=6379

# 布尔值
DEBUG=True
ENABLE_LOGGING=true
```

## 高级用法

### 1. 强制重新加载

```python
from dotenv import load_dotenv
import os

# 强制重新加载，即使已经加载过
load_dotenv(override=True)
```

### 2. 加载多个 .env 文件

```python
from dotenv import load_dotenv
import os

# 加载多个 .env 文件
load_dotenv('.env.default')    # 默认配置
load_dotenv('.env.local')      # 本地配置（会覆盖默认配置）
```

### 3. 错误处理

```python
from dotenv import load_dotenv
import os

try:
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY 未设置")
except Exception as e:
    print(f"加载环境变量时出错: {e}")
```

## 最佳实践

### 1. 在项目入口处加载

```python
# main.py 或 app.py
from dotenv import load_dotenv
import os

# 在应用启动时加载
load_dotenv()

# 其他导入
from your_module import your_class
```

### 2. 提供默认值

```python
# 总是提供默认值，避免 None 值
api_key = os.getenv('OPENAI_API_KEY', '')
model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
debug = os.getenv('DEBUG', 'False').lower() == 'true'
```

### 3. 类型转换

```python
# 正确处理不同类型的配置
max_tokens = int(os.getenv('MAX_TOKENS', '300'))
temperature = float(os.getenv('TEMPERATURE', '0.7'))
debug = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
```

### 4. 验证必要的环境变量

```python
def validate_environment():
    """验证必要的环境变量是否设置"""
    required_vars = ['OPENAI_API_KEY', 'GOOGLE_CLOUD_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}")

# 在应用启动时调用
load_dotenv()
validate_environment()
```

## 测试

运行测试脚本检查环境变量是否正确加载：

```bash
python Tools/utils/web_search_example.py
```

## 注意事项

1. **安全性**：`.env` 文件包含敏感信息，确保它被添加到 `.gitignore` 中
2. **路径**：`load_dotenv()` 默认在当前工作目录查找 `.env` 文件
3. **覆盖**：如果环境变量已经存在，`load_dotenv()` 默认不会覆盖它们
4. **编码**：`.env` 文件应该使用 UTF-8 编码 