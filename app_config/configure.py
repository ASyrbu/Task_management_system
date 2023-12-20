# В файле configure.py
from sanic import Sanic
from json import load
from Task_management_system.app_config.routes import (
    route_add_text, route_get_task_status, route_search_text_by_id
)
from Task_management_system.mongodb.startup import initialize_database
from Task_management_system.functions.filesystem_utils import environment_get
from Task_management_system.app_config.tasks_queue import process_tasks
from Task_management_system.app_config import routes as routing


def read_config() -> dict:
    file_handler = open("app_config/settings.json", "r")
    server_config = load(file_handler)
    file_handler.close()
    return server_config


def get_application():
    app_name = environment_get("SERVICE_NAME")
    sanic_app = Sanic(app_name)
    sanic_app.config.update(
        read_config()
    )

    sanic_app.register_listener(initialize_database, "before_server_start")
    sanic_app.add_route(route_add_text, "/api/addtext", methods=["POST"], ctx_refsanic=sanic_app)
    sanic_app.add_route(route_get_task_status, "/api/taskstatus", methods=["GET"], ctx_refsanic=sanic_app)
    sanic_app.add_route(route_search_text_by_id, "/api/search/text_by_id", methods=["POST"], ctx_refsanic=sanic_app)
    sanic_app.add_route(routing.login_route, "/api/login", methods=["POST"], ctx_refsanic=sanic_app)
    sanic_app.add_route(routing.register_route, "/api/registration", methods=["POST"], ctx_refsanic=sanic_app)
    sanic_app.add_route(routing.check_registration_code_route, "/api/registration/check_code", methods=["POST"], ctx_refsanic=sanic_app)
    sanic_app.add_route(routing.create_registration_code_route, "/api/admin/create_code", methods=["POST"], ctx_refsanic=sanic_app)
    sanic_app.on_response(routing.add_response_headers)
    sanic_app.add_task(process_tasks())

    return sanic_app
