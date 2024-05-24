from flask import Flask, request
from flask_restx import Api
import logging

# Init Flask app
app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Monkey Tools for The Internet",
    description="Monkey Tools for The Internet",
)


@app.before_request
def before_request():
    request.app_id = request.headers.get("x-monkeys-appid")
    request.user_id = request.headers.get("x-monkeys-userid")
    request.team_id = request.headers.get("x-monkeys-teamid")
    request.workflow_id = request.headers.get("x-monkeys-workflowid")
    request.workflow_instance_id = request.headers.get("x-monkeys-workflow-instanceid")


@api.errorhandler(Exception)
def handle_exception(error):
    return {"message": str(error)}, 500


@app.get("/manifest.json")
def get_manifest():
    return {
        "schema_version": "v1",
        "display_name": "Monkey Tools for The Internet",
        "namespace": "monkey_tools_internet",
        "auth": {"type": "none"},
        "api": {"type": "openapi", "url": "/swagger.json"},
        "contact_email": "dev@inf-monkeys.com",
    }

class NoSuccessfulRequestLoggingFilter(logging.Filter):
    def filter(self, record):
        return "GET /" not in record.getMessage()


# 获取 Flask 的默认日志记录器
log = logging.getLogger("werkzeug")
# 创建并添加过滤器
log.addFilter(NoSuccessfulRequestLoggingFilter())

