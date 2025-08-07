
from sanic.response import text
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from sqlalchemy.ext.asyncio import AsyncSession
from co6co_db_ext.db_utils import db_tools
from co6co_permissions.view_model.base_view import AuthMethodView
from co6co_permissions.view_model.aop import exist, ObjectExistRoute
from sqlalchemy.sql import Select
from co6co.utils import log

from ...model.pos.tables import SysTaskPO, DynamicCodePO
from .._filters.sysTask import Filter
from ...service import CustomTask as custom


class ExistView(AuthMethodView):
    routePath = ObjectExistRoute

    async def get(self, request: Request, code: str, pk: int = 0):
        result = await self.exist(request, SysTaskPO.code == code, SysTaskPO.id != pk)
        return exist(result, "任务编码", code)


class SelectViews(AuthMethodView):
    routePath = "/select/<category:int>"

    async def get(self, request: Request, category: int):
        """
        树形选择下拉框数据
        selectTree :  el-Tree
        """
        if category == 0:
            data = custom.get_list()
            all = [{"id": t[1], "name": t[0]}for t in data]
            return self.response_json(Result.success(data=all))
        else:
            select = (
                Select(DynamicCodePO.id, DynamicCodePO.name)
                .filter(DynamicCodePO.state == 1, DynamicCodePO.category == 1)
                .order_by(DynamicCodePO.code.asc())
            )
            return await self.query_list(request, select,  isPO=False)


class Views(AuthMethodView):
    async def get(self, request: Request):
        """
        树形选择下拉框数据
        selectTree :  el-Tree
        """
        select = (
            Select(SysTaskPO.id, SysTaskPO.name, SysTaskPO.code, SysTaskPO.state, SysTaskPO.execStatus)
            .order_by(SysTaskPO.code.asc())
        )
        return await self.query_list(request, select,  isPO=False)

    async def post(self, request: Request):
        """
        树形 table数据
        tree 形状 table
        """
        param = Filter()
        param.__dict__.update(request.json)

        return await self.query_page(request, param)

    async def put(self, request: Request):
        """
        增加
        """
        po = SysTaskPO()
        userId = self.getUserId(request)
        po.__dict__.update(request.json)

        async def before(po: SysTaskPO, session: AsyncSession, request):
            exist = await db_tools.exist(session,  SysTaskPO.code.__eq__(po.code), column=SysTaskPO.id)
            if exist:
                return JSON_util.response(Result.fail(message=f"'{po.code}'已存在！"))

        return await self.add(request, po, json2Po=False, userId=userId, beforeFun=before)


class View(AuthMethodView):
    routePath = "/<pk:int>"

    async def put(self, request: Request, pk: int):
        """
        编辑
        """
        async def before(oldPo: SysTaskPO, po: SysTaskPO, session: AsyncSession, request):
            exist = await db_tools.exist(session, SysTaskPO.id != oldPo.id, SysTaskPO.code.__eq__(po.code), column=SysTaskPO.id)
            if exist:
                return JSON_util.response(Result.fail(message=f"'{po.code}'已存在！"))
            if oldPo.execStatus == 1:
                return JSON_util.response(Result.fail(message=f"'任务正在运行中请先停止，后再进行编辑！"))

        return await self.edit(request, pk, SysTaskPO,  userId=self.getUserId(request), fun=before)

    async def delete(self, request: Request, pk: int):
        """
        删除
        """
        return await self.remove(request, pk, SysTaskPO)
