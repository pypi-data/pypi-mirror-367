from sanic import Blueprint
from co6co_sanic_ext.api import add_routes
from ..view_model. systask.dynamicCodeView import View, Views, ExistView, RunView
from ..view_model. systask.codeView import cronViews, codeView
api_dynamic = Blueprint("dynamicCode_API", url_prefix="/dynamicCode")
add_routes(api_dynamic, ExistView, View, Views, RunView)

# 做一些测试用
api_code = Blueprint("code_API", url_prefix="/code")
add_routes(api_code,  cronViews, codeView)
