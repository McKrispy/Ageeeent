"""
LLM配置管理
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv, set_key
from pathlib import Path

# 直接使用工作区根目录
ENV_FILE_PATH = Path('.env')

# 加载环境变量
load_dotenv()

class LLMConfig:
    """LLM配置类"""

    # 通用配置
    TEMPERATURE = os.getenv('TEMPERATURE')
    MAX_TOKENS = os.getenv('MAX_TOKENS')
    SELECTED_PROVIDER = os.getenv('SELECTED_PROVIDER')
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
    
    # Google配置
    GOOGLE_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY')
    GOOGLE_BASE_URL = os.getenv('GOOGLE_BASE_URL')
    GOOGLE_MODEL = os.getenv('GOOGLE_MODEL')
    
    # Anthropic配置
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    ANTHROPIC_BASE_URL = os.getenv('ANTHROPIC_BASE_URL')
    ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL')
    
    @classmethod
    def get_openai_config(cls) -> Dict[str, Any]:
        """获取OpenAI配置"""
        return {
            'api_key': cls.OPENAI_API_KEY,
            'model': cls.OPENAI_MODEL,
            'base_url': cls.OPENAI_BASE_URL
        }
    
    @classmethod
    def get_google_config(cls) -> Dict[str, Any]:
        """获取Google配置"""
        return {
            'api_key': cls.GOOGLE_API_KEY,
            'model': cls.GOOGLE_MODEL,
            'base_url': cls.GOOGLE_BASE_URL
        }
    
    @classmethod
    def get_anthropic_config(cls) -> Dict[str, Any]:
        """获取Anthropic配置"""
        return {
            'api_key': cls.ANTHROPIC_API_KEY,
            'model': cls.ANTHROPIC_MODEL,
            'base_url': cls.ANTHROPIC_BASE_URL
        }

    @classmethod
    def get_general_config(cls) -> Dict[str, Any]:
        """获取通用配置"""
        return {
            'temperature': cls.TEMPERATURE,
            'max_tokens': cls.MAX_TOKENS,
            'selected_provider': cls.SELECTED_PROVIDER
        }
    
    @classmethod
    def update_openai_config(cls, **kwargs):
        """更新OpenAI配置到.env文件"""
        cls._update_env_file('OPENAI_API_KEY', kwargs.get('api_key'))
        cls._update_env_file('OPENAI_MODEL', kwargs.get('model'))
        cls._update_env_file('OPENAI_BASE_URL', kwargs.get('base_url'))
        load_dotenv(override=True)
        cls._reload_config()
    
    @classmethod
    def update_google_config(cls, **kwargs):
        """更新Google配置到.env文件"""
        cls._update_env_file('GOOGLE_CLOUD_API_KEY', kwargs.get('api_key'))
        cls._update_env_file('GOOGLE_MODEL', kwargs.get('model'))
        cls._update_env_file('GOOGLE_BASE_URL', kwargs.get('base_url'))
        load_dotenv(override=True)
        cls._reload_config()
    
    @classmethod
    def update_anthropic_config(cls, **kwargs):
        """更新Anthropic配置到.env文件"""
        cls._update_env_file('ANTHROPIC_API_KEY', kwargs.get('api_key'))
        cls._update_env_file('ANTHROPIC_MODEL', kwargs.get('model'))
        cls._update_env_file('ANTHROPIC_BASE_URL', kwargs.get('base_url'))
        load_dotenv(override=True)
        cls._reload_config()
    
    @classmethod
    def update_general_config(cls, **kwargs):
        """更新通用配置到.env文件"""
        cls._update_env_file('TEMPERATURE', kwargs.get('temperature'))
        cls._update_env_file('MAX_TOKENS', kwargs.get('max_tokens'))
        cls._update_env_file('SELECTED_PROVIDER', kwargs.get('selected_provider'))
        load_dotenv(override=True)
        cls._reload_config()
    
    @classmethod
    def _update_env_file(cls, key: str, value: Optional[str]):
        """更新.env文件中的特定键值"""
        if value is not None:
            if not ENV_FILE_PATH.exists():
                ENV_FILE_PATH.touch()
            set_key(ENV_FILE_PATH, key, str(value))
    
    @classmethod
    def _reload_config(cls):
        """重新加载配置"""
        cls.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        cls.OPENAI_MODEL = os.getenv('OPENAI_MODEL')
        cls.OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
        
        cls.GOOGLE_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY')
        cls.GOOGLE_MODEL = os.getenv('GOOGLE_MODEL')
        cls.GOOGLE_BASE_URL = os.getenv('GOOGLE_BASE_URL')
        
        cls.ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
        cls.ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL')
        cls.ANTHROPIC_BASE_URL = os.getenv('ANTHROPIC_BASE_URL')

        cls.TEMPERATURE = os.getenv('TEMPERATURE')
        cls.MAX_TOKENS = os.getenv('MAX_TOKENS')
        cls.SELECTED_PROVIDER = os.getenv('SELECTED_PROVIDER')
class DBConfig:
    """DB配置类"""
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
    
    @classmethod
    def get_db_config(cls) -> Dict[str, Any]:
        """获取DB配置"""
        return {
            'host': cls.REDIS_HOST,
            'port': cls.REDIS_PORT,
            'db': cls.REDIS_DB,
            'password': cls.REDIS_PASSWORD
        }

    @classmethod
    def set_db_config(cls, host: str, port: int, db: int, password: str):
        """设置DB配置"""
        cls.REDIS_HOST = host
        cls.REDIS_PORT = port
        cls.REDIS_DB = db
        cls.REDIS_PASSWORD = password
    
    @classmethod
    def update_db_config(cls, **kwargs):
        """更新数据库配置到.env文件"""
        cls._update_env_file('REDIS_HOST', kwargs.get('host'))
        cls._update_env_file('REDIS_PORT', kwargs.get('port'))
        cls._update_env_file('REDIS_DB', kwargs.get('db'))
        cls._update_env_file('REDIS_PASSWORD', kwargs.get('password'))
        load_dotenv(override=True)
        cls._reload_config()
    
    @classmethod
    def _update_env_file(cls, key: str, value: Optional[str]):
        """更新.env文件中的特定键值"""
        if value is not None:
            if not ENV_FILE_PATH.exists():
                ENV_FILE_PATH.touch()
            set_key(ENV_FILE_PATH, key, str(value))
    
    @classmethod
    def _reload_config(cls):
        """重新加载配置"""
        cls.REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
        cls.REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
        cls.REDIS_DB = int(os.getenv('REDIS_DB', '0'))
        cls.REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

class EnvManager:
    """环境变量管理器"""
    
    @staticmethod
    def create_env_file():
        """创建.env文件模板"""
        env_content = """# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_CLOUD_API_KEY=your_google_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Model Configuration
OPENAI_MODEL=gpt-3.5-turbo
GOOGLE_MODEL=gemini-pro
ANTHROPIC_MODEL=claude-3-sonnet-20240229
MAX_TOKENS=300
TEMPERATURE=0.7

# OpenAI Configuration
OPENAI_BASE_URL=https://api.openai.com/v1

# Database Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Other Configuration
DEBUG=False
ENABLE_LOGGING=True
"""
        if not ENV_FILE_PATH.exists():
            with open(ENV_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(env_content)
            print(f"已创建.env文件: {ENV_FILE_PATH.absolute()}")
        else:
            print(f".env文件已存在: {ENV_FILE_PATH.absolute()}")
    
    @staticmethod
    def get_env_file_path() -> Path:
        """获取.env文件路径"""
        return ENV_FILE_PATH
    
    @staticmethod
    def env_file_exists() -> bool:
        """检查.env文件是否存在"""
        return ENV_FILE_PATH.exists()
    
    @staticmethod
    def reload_env():
        """重新加载环境变量"""
        load_dotenv(override=True)

if __name__ == "__main__":
    print(f".env文件路径: {ENV_FILE_PATH.absolute()}")
    
    # 创建.env文件（如果不存在）
    EnvManager.create_env_file()
    
    print("\nLLM配置:")
    print(LLMConfig.get_openai_config())
    print(LLMConfig.get_google_config())
    print(LLMConfig.get_anthropic_config())
    
    print("\n数据库配置:")
    print(DBConfig.get_db_config())
    
    print("\n环境文件状态:")
    print(f".env文件存在: {EnvManager.env_file_exists()}")
    if EnvManager.env_file_exists():
        print(f".env文件路径: {EnvManager.get_env_file_path().absolute()}")