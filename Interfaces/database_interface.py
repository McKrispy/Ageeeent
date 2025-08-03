# -*- coding: utf-8 -*-
"""
此文件定义了与 RedisJSON 数据库交互的接口和具体实现。
"""
import os
import redis
import json
from abc import ABC, abstractmethod
from typing import Any, Dict

class DatabaseInterface(ABC):
    """
    一个抽象基类，定义了与数据库交互的标准方法。
    这里特指用于存储和检索“重型”数据的 RedisJSON 数据库。
    """
    @abstractmethod
    def connect(self):
        """建立与数据库的连接。"""
        pass

    @abstractmethod
    def disconnect(self):
        """断开与数据库的连接。"""
        pass

    @abstractmethod
    def store_data(self, key: str, data: Any) -> str:
        """
        将数据存储到数据库中。

        Args:
            key (str): 数据的唯一标识符。通常格式为 'task_id:data_type:unique_hash'。
            data (Any): 要存储的数据，通常是大型的 JSON 对象或原始文本。

        Returns:
            str: 确认数据存储的键。
        """
        pass

    @abstractmethod
    def retrieve_data(self, key: str) -> Any:
        """
        根据键从数据库中检索数据。

        Args:
            key (str): 要检索的数据的键。

        Returns:
            Any: 检索到的原始数据。
        """
        pass

class RedisJSONInterface(DatabaseInterface):
    """
    与 RedisJSON 数据库交互的具体实现。
    """
    def __init__(self):
        """
        从环境变量初始化Redis连接参数。
        """
        self.host = os.getenv('REDIS_HOST', 'localhost')
        self.port = int(os.getenv('REDIS_PORT', 6379))
        self.db = int(os.getenv('REDIS_DB', 0))
        self.client = None

    def connect(self):
        """
        使用 redis-py 客户端建立与 Redis 服务器的连接。
        """
        try:
            print(f"Connecting to RedisJSON database at {self.host}:{self.port}...")
            self.client = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)
            # 验证连接和 ReJSON 模块可用性
            self.client.ping()
            self.client.json().set("connection_test", "$", {"status": "ok"})
            print("Successfully connected to RedisJSON.")
        except redis.exceptions.ConnectionError as e:
            print(f"Error connecting to Redis: {e}")
            raise

    def disconnect(self):
        """
        断开与 Redis 服务器的连接。
        """
        if self.client:
            print("Disconnecting from RedisJSON database...")
            self.client.close()

    def store_data(self, key: str, data: Any) -> str:
        """
        使用 redis-py 库的 `json.set` 命令将数据存入 RedisJSON。
        """
        if not self.client:
            raise ConnectionError("Database is not connected. Call connect() first.")
        try:
            self.client.json().set(key, "$", data)
            print(f"Successfully stored data with key: {key} in RedisJSON.")
            return key
        except Exception as e:
            print(f"Error storing data in RedisJSON: {e}")
            raise

    def retrieve_data(self, key: str) -> Any:
        """
        使用 redis-py 库的 `json.get` 命令从 RedisJSON 检索数据。
        """
        if not self.client:
            raise ConnectionError("Database is not connected. Call connect() first.")
        try:
            data = self.client.json().get(key)
            print(f"Successfully retrieved data with key: {key} from RedisJSON.")
            return data
        except Exception as e:
            print(f"Error retrieving data from RedisJSON: {e}")
            return None
