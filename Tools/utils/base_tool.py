from abc import ABC, abstractmethod
from typing import Any

class BaseTool(ABC):
    """
    所有工具的抽象基类。
    """
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        执行工具的具体逻辑。

        Returns:
            Any: 工具执行后返回的原始数据（例如，网页HTML，API响应的JSON）。
        """
        pass