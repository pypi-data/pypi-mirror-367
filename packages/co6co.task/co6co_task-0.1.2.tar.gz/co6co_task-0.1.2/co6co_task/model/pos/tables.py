from __future__ import annotations
from co6co_db_ext.po import BasePO, UserTimeStampedModelPO, TimeStampedModelPO
from sqlalchemy import func, INTEGER, DATE, FLOAT, DOUBLE, SMALLINT, Integer, UUID, Text, INTEGER, BigInteger, Column, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship, declarative_base, Relationship
import co6co.utils as tool
from co6co.utils import hash
import sqlalchemy
from sqlalchemy.schema import DDL
from sqlalchemy import MetaData
from sqlalchemy.dialects.mysql import VARCHAR


class SysTaskPO(UserTimeStampedModelPO):
    __tablename__ = "tb_task"
    id = Column("id", Integer, comment="主键",  autoincrement=True, primary_key=True)
    name = Column("name", String(64),  comment="任务名称")
    code = Column("code", String(64),  comment="任务编码")
    category = Column("category", Integer, comment="0:系统-系统中选择,10:用户-用户编写来自tb_dynamic_code表中的")
    data = Column("ass_data", String(128), comment="关联数据,0:本程序中编译代码,1:关联数据tb_dynamic_code表中的Id")
    state = Column("state", Integer, comment="任务状态")
    execStatus = Column("status", Integer, comment="运行状态")
    cron = Column("cron", String(128), comment="cron表达式")

    def update(self, po: SysTaskPO):
        self.name = po.name
        self.code = po.code
        self.state = po.state
        self.category = po.category
        self.data = po.data
        self.cron = po.cron
        self.execStatus = po.execStatus


class DynamicCodePO(UserTimeStampedModelPO):
    """
    动态代码， 
    """
    __tablename__ = "tb_dynamic_code"
    id = Column("id", Integer, comment="主键",  autoincrement=True, primary_key=True)
    name = Column("name", String(64),  comment="代码名称")
    code = Column("code", String(64),  comment="代码编码")
    category = Column("category", Integer, comment="0:python")
    # 增加触发器涉及的逻辑较多，使用 cron 表达式 可以完全替代相关需求
    # trigger = Column("trigger", String(16), comment="date|interval|cron")

    state = Column("state", Integer, comment="任务状态")
    sourceCode = Column("source_code", String(4096), comment="执行代码")

    def update(self, po: DynamicCodePO):
        self.name = po.name
        self.category = po.category
        self.code = po.code
        self.state = po.state
        self.sourceCode = po.sourceCode
