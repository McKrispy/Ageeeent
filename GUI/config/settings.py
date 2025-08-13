import streamlit as st
import json
import os
from typing import Dict, Any

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_file = "llm_config.json"
        self.default_config = {
            "models": {
                "gpt-4": "GPT-4",
                "gpt-3.5-turbo": "GPT-3.5 Turbo",
                "claude-3-opus": "Claude 3 Opus",
                "claude-3-sonnet": "Claude 3 Sonnet",
                "gemini-pro": "Gemini Pro"
            },
            "selected_model": "gpt-3.5-turbo",
            "api_keys": {
                "openai": "",
                "anthropic": "",
                "google": ""
            },
            "default_prompts": [
                "你好，请介绍一下你自己",
                "请解释一下什么是人工智能",
                "写一个Python函数来计算斐波那契数列"
            ]
        }
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"保存配置失败: {e}")

def load_config() -> Dict[str, Any]:
    """加载配置的便捷函数"""
    config_manager = ConfigManager()
    return config_manager.load_config()

def save_config(config: Dict[str, Any]):
    """保存配置的便捷函数"""
    config_manager = ConfigManager()
    config_manager.save_config(config)
