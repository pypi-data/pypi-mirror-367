from sanic.response import text
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select, Update
from co6co_db_ext.db_utils import db_tools
from co6co_permissions.view_model.base_view import AuthMethodView
from co6co_web_db.view_model import get_one
from ...model.pos.tables import DynamicCodePO, SysTaskPO
from datetime import datetime
from co6co_permissions.model.enum import dict_state
from co6co.utils import log, DATA

from multiprocessing.connection import PipeConnection
from ...model.enum import CommandCategory
from .codeView import _codeView
from ...service import CustomTask as custom
from co6co.task.pools import timeout


class schedView(_codeView, AuthMethodView):
    routePath = "/sched/<pk:int>"

    async def read_data(self, pk: int, request: Request):
        """
        从数据库中读取 code ,sourceCode,cron
        """
        select = (
            Select(SysTaskPO.code, SysTaskPO.category, SysTaskPO.cron, DynamicCodePO.sourceCode, SysTaskPO.data)
            .outerjoin(DynamicCodePO, DynamicCodePO.id == SysTaskPO.data)
            .filter(SysTaskPO.id.__eq__(pk))
        )

        poDict: dict = await db_tools.execForMappings(self.get_db_session(request), select, queryOne=True)
        code = poDict.get("code")
        sourceCode = poDict.get("sourceCode")
        data = poDict.get("data")
        log.warn("sourceCode:", sourceCode)
        cron = poDict.get("cron")
        return code, cron, sourceCode, data

    @staticmethod
    def getPipConn(request: Request) -> PipeConnection:
        return request.app.ctx.child_conn

    async def post(self, request: Request, pk: int):
        """
        调度
        周期性执行的可以执行完成的代码
        """
        code,  cron, sourceCode, data = await self.read_data(pk, request)
        conn = schedView.getPipConn(request)
        conn.send(CommandCategory.createOption(CommandCategory.Exist, code=code))
        result: DATA = conn.recv()
        param = {"code": code, "sourceCode": sourceCode, "sourceForm": data, "cron": cron}
        if result.success:
            param.update({"command": CommandCategory.MODIFY})
        else:
            param.update({"command": CommandCategory.START})

        conn.send(CommandCategory.createOption(**param))
        result: DATA = conn.recv()
        res = result.success
        if res:
            return self.response_json(Result.success())
        else:
            return self.response_json(Result.fail(message=result.data))

    @staticmethod
    async def execCommand(request: Request, code: str, command: CommandCategory):
        """
        执行一些简单命令
        """
        conn = schedView.getPipConn(request)
        conn.send(CommandCategory.createOption(command, code=code))
        result: DATA = conn.recv()
        if result.success:
            return True, result.data
        else:
            return False, result.data

    async def patch(self, request: Request, pk: int):
        """
        查询下一次运行时间
        """
        select = Select(SysTaskPO).filter(SysTaskPO.id.__eq__(pk))
        po: SysTaskPO = await get_one(request, select)
        success, data = await schedView.execCommand(request, po.code, CommandCategory.GETNextTime)
        if success:
            return self.response_json(Result.success(data, message="获取成功"))
        else:
            return self.response_json(Result.fail(message="获取失败:"+data))

    async def delete(self, request: Request, pk: int):
        """
        停止调度
        """
        select = Select(SysTaskPO).filter(SysTaskPO.id.__eq__(pk))
        po: SysTaskPO = await get_one(request, select)
        success, msg = await schedView.execCommand(request, po.code, CommandCategory.STOP)
        if success:
            return self.response_json(Result.success(message="停止成功"))
        else:
            return self.response_json(Result.fail(message="停止失败:"+msg))

    async def put(self, request: Request, pk: int):
        """
        执行一次
        """
        _,  _, sourceCode, data = await self.read_data(pk, request)
        isTimeout = False
        secounds = 4
        result = Result.success()
        if not sourceCode:
            try:
                task = custom.get_task(data)
                isTimeout, _ = timeout(secounds, task.main)
                log.warn("执行成功", isTimeout)
            except Exception as e:
                log.err("执行失败", e)
                return self.response_json(Result.fail(e, message="执行失败"))
        else:
            isTimeout, result = timeout(secounds,  self.exec_py_code, False, sourceCode)
        if isTimeout:
            return self.response_json(Result.success(data="执行时间过长", message="执行时间过长！"))
        else:
            return self.response_json(result)
