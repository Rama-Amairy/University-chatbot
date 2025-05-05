import os
import sys
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

FILE_LOCATION = f"{os.path.dirname(__file__)}/upload_file.py"

# Add root dir and handle potential import errors
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from helpers import get_settings, Settings
    from controllers import create_unique_name

except Exception as e:
    msg = f"Import Error in: {FILE_LOCATION}, Error: {e}"
    raise ImportError(msg)

upload_route = APIRouter()

UPLOAD_DIR = get_settings().LOC_DOC
os.makedirs(UPLOAD_DIR, exist_ok=True)


@upload_route.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
):
    try:
        # Generate a unique file name
        unique_filename = create_unique_name(file.filename)
        file_location = os.path.join(UPLOAD_DIR, unique_filename)

        # Save the file to disk
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        log_info(f"File uploaded and saved as '{unique_filename}' at '{file_location}'")

        return JSONResponse(
            status_code=200,
            content={
                "message": "File uploaded successfully.",
                "filename": unique_filename,
                "saved_to": file_location
            }
        )

    except Exception as e:
        log_error(f"Failed to upload file '{file.filename}': {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File upload failed.")