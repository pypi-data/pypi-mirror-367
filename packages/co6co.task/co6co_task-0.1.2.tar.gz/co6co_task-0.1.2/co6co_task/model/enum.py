
from __future__ import annotations
from co6co.enums import Base_Enum

from co6co.utils import DATA


class CommandCategory(Base_Enum):
    """
    操作类别
    """
    GET = "get", 0  # 获取数据
    Exist = "exist", 1  # 任务是否存在
    START = "start", 2  # 启动任务
    STOP = "stop", 3  # 停止任务
    REMOVE = "remove", 4  # 移除任务
    DELETE = "DELETE", 4  # 移除任务
    RESTART = "restart", 5  # 重启任务
    MODIFY = "modify", 6  # 修改任务
    GETNextTime = "nextTime", 7  # 获取下一次执行时间

    @staticmethod
    def createOption(command: CommandCategory, data: str = "", success: bool = True, **kwarg) -> DATA:
        return DATA(command=command, data=data, success=success, **kwarg)
