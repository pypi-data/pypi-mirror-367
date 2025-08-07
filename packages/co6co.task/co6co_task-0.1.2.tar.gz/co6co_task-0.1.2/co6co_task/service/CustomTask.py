
from __future__ import annotations
from abc import ABC, abstractmethod
# 定义接口
from typing import overload, List, Tuple
from co6co.utils import log


class ICustomTask(ABC):
    """
    需要任务类实现该类，才能被识别为任务
    """
    name = "抽象任务接口"
    code = "ICustomTask"
    _isQuit: bool = None

    def __init__(self):
        super().__init__()
        self._isQuit = False

    @abstractmethod
    def main(self):
        pass

    @property
    def isQuit(self) -> bool:
        return self._isQuit

    def stop(self):
        self._isQuit = True
        pass


"""
获取所有子类的列表
"""


@overload
def get_all_subclasses():
    """
    获取所有子类的列表
    """
    pass


def get_all_subclasses(cls=ICustomTask):
    """
    获取所有子类的列表
    """
    all_subclasses = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


def get_list() -> List[Tuple[str, str]]:
    """
    获取所有子类的列表
    [(name,code),]
    """
    class_arr = get_all_subclasses()
    _list = [(c.name, c.code)for c in class_arr]
    return _list


def get_task(code: str) -> ICustomTask | None:
    """
    获取所有子类的列表"
    """
    class_arr = get_all_subclasses()
    for c in class_arr:
        if c.code == code:
            try:
                return c()
            except Exception as e:
                log.err(f"实例化'{c}'失败", e)
    return None
