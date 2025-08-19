# -*- coding: utf-8 -*-
"""
此文件定义了与大型语言模型 (LLM) API 交互的接口。
它提供了一个抽象基类，用于统一不同 LLM 提供商（如 OpenAI, Google Cloud）的调用方式。
"""
import os
from abc import ABC, abstractmethod
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv
from anthropic import Anthropic

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
        初始化OpenAI接口，从环境变量获取API密钥和可选的Base URL
        """
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        base_url = os.getenv('OPENAI_BASE_URL') # 可选，用于代理或非官方端点
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    
    def get_completion(self, prompt: str, model: str = "gpt-4o-mini", **kwargs) -> str:
        """
        使用 OpenAI API 获取文本补全。

        Args:
            prompt (str): 发送给 LLM 的提示。
            model (str, optional): 指定要使用的模型。
            **kwargs: 其他API参数，例如 temperature, max_tokens。

        Returns:
            str: LLM 生成的文本响应。
        """
        # 优先使用环境变量中的模型，如果没有则使用传入的默认值
        env_model = os.getenv('OPENAI_MODEL')
        if env_model:
            model = env_model
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"An error occurred with OpenAI API: {e}")
            return ""

class GoogleCloudInterface(LLMAPIInterface):
    """
    与 Google AI (Gemini) API 交互的具体实现。
    注意：这使用 google-generativeai 库，它通过 API 密钥进行身份验证。
    """
    def __init__(self):
        """
        初始化Google AI接口，从环境变量获取API密钥
        """
        load_dotenv()
        api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
        base_url = os.getenv('GOOGLE_BASE_URL')
        if not api_key:
            raise ValueError("GOOGLE_CLOUD_API_KEY environment variable is required")
        genai.configure(api_key=api_key)

    
    def get_completion(self, prompt: str, model: str = "gemini-1.5-flash", **kwargs) -> str:
        """
        使用 Google AI API 获取文本补全。

        Args:
            prompt (str): 发送给 LLM 的提示。
            model (str, optional): 指定要使用的模型。Defaults to "gemini-pro".
            **kwargs: 其他API参数，例如 temperature, max_output_tokens,
                      封装在 'generation_config' 字典中。

        Returns:
            str: LLM 生成的文本响应。
        """
        # 优先使用环境变量中的模型，如果没有则使用传入的默认值
        env_model = os.getenv('GOOGLE_MODEL')
        if env_model:
            model = env_model
            
        try:
            model_instance = genai.GenerativeModel(model_name=model)
            
            # 适配kwargs以符合google-generativeai的generation_config
            generation_config = {}
            if 'temperature' in kwargs:
                generation_config['temperature'] = kwargs['temperature']
            if 'max_tokens' in kwargs:
                generation_config['max_output_tokens'] = kwargs['max_tokens']
            
            response = model_instance.generate_content(
                prompt,
                generation_config=generation_config if generation_config else None
            )
            return response.text
        except Exception as e:
            print(f"An error occurred with Google AI API: {e}")
            return ""

class AnthropicInterface(LLMAPIInterface):
    """
    与 Anthropic API 交互的具体实现。
    """
    def __init__(self):
        """
        初始化Anthropic接口，从环境变量获取API密钥
        """
        load_dotenv()
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        base_url = os.getenv('ANTHROPIC_BASE_URL')
        self.client = Anthropic(api_key=api_key, base_url=base_url)

    def get_completion(self, prompt: str, model: str = "claude-3-5-sonnet-20240620", **kwargs) -> str:
        """
        使用 Anthropic API 获取文本补全。
        """
        # 优先使用环境变量中的模型，如果没有则使用传入的默认值
        env_model = os.getenv('ANTHROPIC_MODEL')
        if env_model:
            model = env_model
            
        try:
            response = self.client.messages.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            print(f"An error occurred with Anthropic API: {e}")
            return ""

# ==============================================================================
# API 参数信息
# ==============================================================================

"""
--------------------------------------------------------------------------------
OpenAI API (Chat Completions) - 主要参数
--------------------------------------------------------------------------------
通过 client.chat.completions.create(**kwargs) 调用。

- model (str, required):
  要使用的模型ID，例如 "gpt-4", "gpt-3.5-turbo"。

- messages (list[dict], required):
  描述对话的消息列表。每个字典包含 'role' (e.g., "system", "user", "assistant")
  和 'content' (消息文本)。

- temperature (float, optional, default=1.0):
  控制随机性的参数，介于 0.0 和 2.0 之间。较高的值（如 0.8）会使输出更随机，
  而较低的值（如 0.2）会使其更具确定性。

- max_tokens (int, optional, default=inf):
  生成的补全内容中允许的最大token数。

- top_p (float, optional, default=1.0):
  一种替代温度采样的方法，称为核心采样（nucleus sampling）。模型会考虑概率质量为
  top_p 的token的结果。例如，0.1 意味着只考虑构成前10%概率质量的token。

- n (int, optional, default=1):
  为每个输入消息生成多少个聊天补全选项。

- stream (bool, optional, default=False):
  如果为True，将以流式传输部分消息增量。

- stop (str | list[str], optional):
  一个或最多四个序列，API 将在这些序列处停止生成更多token。

- presence_penalty (float, optional, default=0):
  介于-2.0和2.0之间的数字。正值会根据新token是否已在文本中出现来惩罚它们，
  从而增加模型谈论新主题的可能性。

- frequency_penalty (float, optional, default=0):
  介于-2.0和2.0之间的数字。正值会根据新token在文本中的现有频率来惩罚它们，
  从而降低模型逐字重复相同行的可能性。

- logit_bias (dict, optional):
  修改指定token出现在补全中的可能性。接受一个将token（由其在分词器中的token ID指定）
  映射到从-100到100的关联偏置值的json对象。

- user (str, optional):
  代表最终用户的唯一标识符，可以帮助OpenAI监控和检测滥用行为。

官方文档: https://platform.openai.com/docs/api-reference/chat/create

--------------------------------------------------------------------------------
Google AI (Gemini) API - 主要参数
--------------------------------------------------------------------------------
通过 GenerativeModel.generate_content(prompt, generation_config=...) 调用。
generation_config 是一个包含以下参数的字典。

- temperature (float, optional):
  控制随机性的参数，范围 [0.0, 1.0]。较高的值会产生更具创造性的输出，而较低的值会
  产生更直接的响应。

- max_output_tokens (int, optional):
  生成的响应中允许的最大token数。

- top_p (float, optional):
  核心采样。模型从累积概率超过 top_p 的最高概率token中进行选择。

- top_k (int, optional):
  模型从 top_k 个最高概率的token中进行选择。

- candidate_count (int, optional):
  要返回的生成响应的数量。

- stop_sequences (list[str], optional):
  指定一个序列列表，在生成到该序列时模型将停止输出。

官方文档: https://ai.google.dev/api/python/google/generativeai/GenerativeModel#generate_content
"""
