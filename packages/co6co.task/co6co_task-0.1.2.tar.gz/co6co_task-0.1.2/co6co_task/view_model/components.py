

from sanic.response import text
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select
from co6co_permissions.view_model.base_view import AuthMethodView
from model.pos.tables import DynamicCodePO
from co6co_permissions.model.enum import dict_state


class componentViews(AuthMethodView):
    routePath = "/<code:str>"

    async def get(self, request: Request, code: str):
        """
        获取组件代码
        """
        select = Select(DynamicCodePO.sourceCode).filter(DynamicCodePO.code == code, DynamicCodePO.state == dict_state.enabled.val)
        return await self.get_one(request, select, isPO=False)
