from sanic import Sanic, Blueprint, Request
from .syscode import api_dynamic, api_code
from .sysTask import task_api

tasks_api = Blueprint.group(api_dynamic, api_code, task_api,  url_prefix="/tasks")
