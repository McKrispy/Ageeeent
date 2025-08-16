"""
LLM配置管理
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LLMConfig:
    """LLM配置类"""
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('DEFAULT_OPENAI_MODEL', 'gpt-4')
    OPENAI_MAX_TOKENS = int(os.getenv('MAX_TOKENS', '4096'))
    OPENAI_TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
    # Google配置
    GOOGLE_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY')
    GOOGLE_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    GOOGLE_MODEL = os.getenv('DEFAULT_GOOGLE_MODEL', 'gemini-pro')
    
    # Anthropic配置
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    ANTHROPIC_MODEL = os.getenv('DEFAULT_ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
    
    @classmethod
    def get_openai_config(cls) -> Dict[str, Any]:
        """获取OpenAI配置"""
        return {
            'api_key': cls.OPENAI_API_KEY,
            'model': cls.OPENAI_MODEL,
            'max_tokens': cls.OPENAI_MAX_TOKENS,
            'temperature': cls.OPENAI_TEMPERATURE
        }
    
    @classmethod
    def get_google_config(cls) -> Dict[str, Any]:
        """获取Google配置"""
        return {
            'api_key': cls.GOOGLE_API_KEY,
            'project_id': cls.GOOGLE_PROJECT_ID,
            'model': cls.GOOGLE_MODEL
        }
    
    @classmethod
    def get_anthropic_config(cls) -> Dict[str, Any]:
        """获取Anthropic配置"""
        return {
            'api_key': cls.ANTHROPIC_API_KEY,
            'model': cls.ANTHROPIC_MODEL
        }
