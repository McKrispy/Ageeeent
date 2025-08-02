# -*- coding: utf-8 -*-
"""
此文件定义了与大型语言模型 (LLM) API 交互的接口。
它提供了一个抽象基类，用于统一不同 LLM 提供商（如 OpenAI, Google Cloud）的调用方式。
"""
import os
from abc import ABC, abstractmethod

class LLMAPIInterface(ABC):
    """
    一个抽象基类，定义了与任何 LLM API 进行交互的标准。
    所有具体的 LLM API 实现都应继承此类并实现其方法。
    """

    @abstractmethod
    def get_completion(self, prompt: str, model: str = None, **kwargs) -> str:
        """
        从 LLM 获取文本补全。

        Args:
            prompt (str): 发送给 LLM 的提示。
            model (str, optional): 指定要使用的模型。Defaults to None.
            **kwargs: 其他特定于 API 的参数 (e.g., temperature, max_tokens).

        Returns:
            str: LLM 生成的文本响应。
        """
        pass

class OpenAIInterface(LLMAPIInterface):
    """
    与 OpenAI API 交互的具体实现。
    """
    def __init__(self):
        """
        初始化OpenAI接口，从环境变量获取API密钥
        """
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def get_completion(self, prompt: str, model: str = "gpt-4", **kwargs) -> str:
        """
        使用 OpenAI API 获取文本补全。

        具体的实现将在这里编写，包括初始化客户端、发送请求和处理响应。
        """
        # 实际实现将在这里
        print(f"Connecting to OpenAI with model {model} using API key: {self.api_key[:10]}...")
        pass

class GoogleCloudInterface(LLMAPIInterface):
    """
    与 Google Cloud (e.g., Vertex AI) API 交互的具体实现。
    """
    def __init__(self):
        """
        初始化Google Cloud接口，从环境变量获取API密钥
        """
        self.api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        if not self.api_key:
            raise ValueError("GOOGLE_CLOUD_API_KEY environment variable is required")
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT_ID environment variable is required")
    
    def get_completion(self, prompt: str, model: str = "gemini-pro", **kwargs) -> str:
        """
        使用 Google Cloud API 获取文本补全。

        具体的实现将在这里编写，包括认证、发送请求和处理响应。
        """
        # 实际实现将在这里
        print(f"Connecting to Google Cloud with model {model} using API key: {self.api_key[:10]}...")
        pass
