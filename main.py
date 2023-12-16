from app_config.configure import get_application
from functions.filesystem_utils import environment_set as es
from app_config.routes import route_get_task_status
es("SERVICE_NAME", "TASK_MANAGER_API")
sanic_task = get_application()


def run_api():
    get_option = sanic_task.config.get
    sanic_task.run(
        host=get_option("HOST"),
        port=get_option("PORT"),
        workers=get_option("WORKERS"),
        fast=get_option("FAST"),
        debug=get_option("DEBUG")
    )


if __name__ == "__main__":
    sanic_task.add_route(route_get_task_status, "/api/task/status", methods=["GET"])

    run_api()
