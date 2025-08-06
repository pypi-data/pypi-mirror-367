"""标准工作流

标准工作流执行器, 例如:

- 检索可提交的 Alpha
- 鲁棒性检测
- 用户表现分析
"""

import logging
from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Generic, Self, TypeVar

from ..agent import NifflerAgent

Node = TypeVar("Node", bound=Callable[..., Any])


class Pipeline(Generic[Node], metaclass=ABCMeta):
    def __init__(self, agent: NifflerAgent) -> None:
        self.agent = agent
        self.node: list[Node] = []
        self._logger = logging.getLogger(__name__)

    def register(self, node: Node | list[Node]) -> Self:
        if isinstance(node, list):
            self.node += node
        else:
            self.node.append(node)

        return self

    @abstractmethod
    def run(self, *args, **kwargs) -> Any: ...

    def __call__(self, *args, **kwargs) -> Any:
        return self.run(*args, **kwargs)
