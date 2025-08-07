
from sanic.response import text
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select
from co6co_db_ext.db_utils import db_tools
from co6co_permissions.view_model.base_view import AuthMethodView
from ...model.pos.tables import DynamicCodePO
from .._filters.dynamic import Filter
from co6co_permissions.view_model.aop import exist, ObjectExistRoute
from .codeView import _codeView

from co6co_web_db.view_model import get_one
from co6co.utils import log


class ExistView(AuthMethodView):
    routePath = ObjectExistRoute

    async def get(self, request: Request, code: str, pk: int = 0):
        result = await self.exist(request, DynamicCodePO.code == code, DynamicCodePO.id != pk)
        return exist(result, "编码", code)


class Views(AuthMethodView):
    async def get(self, request: Request):
        """
        树形选择下拉框数据
        selectTree :  el-Tree
        """
        select = (
            Select(DynamicCodePO.id, DynamicCodePO.name, DynamicCodePO.code, DynamicCodePO.state)
            .filter(DynamicCodePO.state == 1, DynamicCodePO.category == 1)
            .order_by(DynamicCodePO.code.asc())
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
        po = DynamicCodePO()
        userId = self.getUserId(request)
        po.__dict__.update(request.json)

        async def before(po: DynamicCodePO, session: AsyncSession, request):
            exist = await db_tools.exist(session,  DynamicCodePO.code.__eq__(po.code), column=DynamicCodePO.id)
            if exist:
                return JSON_util.response(Result.fail(message=f"'{po.code}'已存在！"))

        return await self.add(request, po, json2Po=False, userId=userId, beforeFun=before)


class View(AuthMethodView):
    routePath = "/<pk:int>"

    async def put(self, request: Request, pk: int):
        """
        编辑
        """
        async def before(oldPo: DynamicCodePO, po: DynamicCodePO, session: AsyncSession, request):
            exist = await db_tools.exist(session, DynamicCodePO.id != oldPo.id, DynamicCodePO.code.__eq__(po.code), column=DynamicCodePO.id)
            if exist:
                return JSON_util.response(Result.fail(message=f"'{po.code}'已存在！"))
        return await self.edit(request, pk, DynamicCodePO,  userId=self.getUserId(request), fun=before)

    async def delete(self, request: Request, pk: int):
        """
        删除
        """
        return await self.remove(request, pk, DynamicCodePO)


class RunView(_codeView, AuthMethodView):
    routePath = "/run/<pk:int>"

    async def put(self, request: Request, pk: int):
        """
        执行一次
        """
        select = Select(DynamicCodePO).filter(DynamicCodePO.id.__eq__(pk))
        po: DynamicCodePO = await get_one(request, select)
        return self.response_json(self.exec_py_code(po.sourceCode))
