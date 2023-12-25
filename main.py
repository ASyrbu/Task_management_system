from app_config.configure import get_application

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
    run_api()
