from sanic import Sanic, Blueprint, Request
from co6co_sanic_ext.api import add_routes
from ..view_model.systask import View, Views, ExistView, SelectViews
from ..view_model.systask.schedView import schedView

task_api = Blueprint("sysTask_API", url_prefix="/task")
add_routes(task_api, ExistView, View, Views, SelectViews, schedView)
