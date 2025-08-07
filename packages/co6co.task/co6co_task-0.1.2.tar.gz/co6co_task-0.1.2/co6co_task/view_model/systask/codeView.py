

from sanic.response import text
from sanic import Request
from co6co_sanic_ext.model.res.result import Result
from co6co_permissions.view_model.base_view import AuthMethodView
from datetime import datetime
from ...service import Scheduler, CuntomCronTrigger


class cronViews(AuthMethodView):
    routePath = "/cron/test"

    async def _post(self, cron: str):
        if cron == None:
            return Result.success(data=False, message="cron 必须填写")
        else:
            try:
                x = CuntomCronTrigger.resolvecron(cron)
                now = datetime.now()
                next = x.get_next_fire_time(now, now)
                return self.response_json(Result.success(data=True, message="解析成功：当前时间:{},下载执行时间：{}".format(now, next)))
            except Exception as e:
                return self.response_json(Result.success(data=False, message="解析'{}'出错:'{}'".format(cron, e)))

    async def get(self, request: Request):
        """
        cron 表达式 合法性检测
        ?cron=0 0 0 12 12 *
        """
        data = self.usable_args(request)
        cron = data.get("cron", None)
        return await self._post(cron)

    async def post(self, request: Request):
        """
        cron 表达式 合法性检测
        json:{cron:'0 0 0 12 12 *'}
        """
        json: dict = request.json
        cron = json.get("cron", None)
        return await self._post(cron)


class _codeView:
    def exec_py_code(self, pyCode: str):
        """
        运行PyCode
        """
        try:
            res, _e = Scheduler.parseCode(pyCode)
            if res:
                res = _e()
                return Result.success(data=res)
            else:
                return Result.fail(message="解析出错：{}".format(e))
        except Exception as e:
            return Result.fail(message="执行出错：{}".format(e))


class codeView(_codeView, AuthMethodView):
    routePath = "/test"

    async def post(self, request: Request):
        """
        检查代码 python 代码

        params: {code:'python 代码'}
        return {data:False|True,...}
        """
        json: dict = request.json
        code = json.get("code", None)
        res, _e = Scheduler.parseCode(code)
        if res:
            return self.response_json(Result.success(data=True))
        return self.response_json(Result.success(data=False, message="解析代码出错:'{}'".format(_e)))

    async def put(self, request: Request):
        """
        执行代码
        params: {code:'python 代码'}
        return {data:False|True,...}
        """
        json: dict = request.json
        code = json.get("code", None)
        return self.response_json(self.exec_py_code(code))
