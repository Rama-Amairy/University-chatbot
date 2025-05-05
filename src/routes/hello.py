import os
import sys
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

FILE_LOCATION = f"{os.path.dirname(__file__)}/hello.py"
# Add root dir and handle potential import errors
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from helpers import get_settings, Settings
    from enums import HelloResponse
except Exception as e:
    msg = f"Import Error in: {FILE_LOCATION}, Error: {e}"
    raise ImportError(msg)

# Define the router
hello_routes = APIRouter()

@hello_routes.get("/hello")
async def say_hello(app_settings: Settings = Depends(get_settings)):
    try:
        name_app = app_settings.APP_NAME
        version_app = app_settings.APP_VERSION

        log_info(f"App info retrieved: {name_app} {version_app}")
        return JSONResponse(
            content={
                "App Name": name_app,
                "Version": version_app,
                "Message": HelloResponse.APIRUN.value
            }
        )
    except Exception as e:
        log_error(f"Failed to retrieve app info: {e},Error Location: {FILE_LOCATION} ")
        return JSONResponse(
            content={
                "App Name": "Unknown",
                "Version": "Unknown",
                "Message": HelloResponse.APIBREAK.value
            },
            status_code=500
        )