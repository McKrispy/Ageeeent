# -*- coding: utf-8 -*-
"""
此文件定义了与 RedisJSON 数据库交互的接口和具体实现。
"""
import os
import redis
import json
import uuid
from abc import ABC, abstractmethod
from typing import Any
from dotenv import load_dotenv

# 用于存储所有会话ID的Redis集合的键名
SESSIONS_SET_KEY = "agent_sessions_set"

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
        """
        pass

    @abstractmethod
    def retrieve_data(self, key: str) -> Any:
        """
        根据键从数据库中检索数据。
        """
        pass

    @abstractmethod
    def create_new_session_id(self) -> str:
        """
        创建一个新的、唯一的会话ID，并将其存入Redis以备查验。
        """
        pass

class RedisClient(DatabaseInterface):
    """
    与 RedisJSON 数据库交互的具体实现。
    这个客户端应该在应用程序的生命周期内被实例化一次，
    并在需要访问数据库的组件之间共享。
    """
    def __init__(self):
        """
        从环境变量初始化Redis连接参数。
        """
        load_dotenv()
        self.host = os.getenv('REDIS_HOST')
        self.port = int(os.getenv('REDIS_PORT'))
        self.db = int(os.getenv('REDIS_DB'))
        self.connect()

    def connect(self):
        """
        使用 redis-py 客户端建立与 Redis 服务器的连接。
        """
        try:
            print(f"Connecting to RedisJSON database at {self.host}:{self.port}...")
            self.client = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)
            self.client.ping()
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
            self.client = None

    def store_data(self, key: str, data: Any) -> str:
        """
        使用 redis-py 库的 `json.set` 命令将数据存入 RedisJSON。
        """
        if not self.client:
            raise ConnectionError("Database is not connected. Call connect() first.")
        try:
            # 使用 `$` 路径将整个 `data` 对象作为JSON文档存入
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

    def create_new_session_id(self) -> str:
        """
        生成一个唯一的会话ID，并将其添加到一个Redis集合中以确保唯一性。
        """
        if not self.client:
            raise ConnectionError("Database is not connected. Call connect() first.")
        
        while True:
            session_id = f"session_{uuid.uuid4()}"
            # SADD 返回1表示新元素被添加，0表示元素已存在。
            # 这提供了一个原子操作来检查和添加。
            if self.client.sadd(SESSIONS_SET_KEY, session_id):
                print(f"Created and stored new session ID: {session_id}")
                return session_id
