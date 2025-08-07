

from sqlalchemy .orm.attributes import InstrumentedAttribute
from typing import Tuple
from co6co_db_ext.db_filter import absFilterItems
from co6co.utils import log
from sqlalchemy import func, or_, and_, Select
from ...model.pos.tables import DynamicCodePO


class Filter(absFilterItems):
    """
    动态代码 filter
    """
    name: str = None
    code: str = None
    state: int = None

    def __init__(self):
        super().__init__(DynamicCodePO)

    def filter(self) -> list:
        """
        过滤条件
        """
        filters_arr = []
        if self.checkFieldValue(self.name):
            filters_arr.append(DynamicCodePO.name.like(f"%{self.name}%"))
        if self.checkFieldValue(self.code):
            filters_arr.append(DynamicCodePO.code.like(f"%{self.code}%"))
        if self.checkFieldValue(self.state):
            filters_arr.append(DynamicCodePO.state.__eq__(self.state))
        return filters_arr

    def getDefaultOrderBy(self) -> Tuple[InstrumentedAttribute]:
        """
        默认排序
        """
        return (DynamicCodePO.createTime.desc(),)
