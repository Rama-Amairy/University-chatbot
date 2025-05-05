from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from pathlib import Path
import sys
import sqlite3 as sql3

from src.logs.logger import log_warning

FILE_LOCATION = str(Path(__file__).resolve())

try:
    MAIN_DIR = Path(__file__).resolve().parent.parent
    sys.path.append(str(MAIN_DIR))

    from logs import log_error, log_info
    from controllers import from_doc_to_chunks, clear
    from schemes import ChunkRequest
    from dbs import add_chunk
except Exception as e:
    raise ImportError(f"Import Error in: {FILE_LOCATION}, Error: {e}")

def get_db_conn(request: Request):
    """Retrieve the relational database connection from the app state."""
    conn = request.app.state.conn
    if not conn:
        log_warning("Relational database connection not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Relational database service is not available."
        )
    return conn

to_chunks_route = APIRouter()


@to_chunks_route.post("/to_chunks")
async def to_chunks(request: Request,
                    body: ChunkRequest,
                    conn:sql3.Connection = Depends(get_db_conn)):
    """
    Converts documents into text chunks and stores them in the SQLite database.
    """
    file_path = body.file_path
    do_reset = body.do_reset

    log_info(f"Starting chunking for: {file_path or '[ALL DOCUMENTS]'}")

    try:
        if do_reset:
            clear(conn=conn, table_name="chunks")
            log_info("Chunks table cleared.")

        df = from_doc_to_chunks(file_path=file_path)

        if df.empty:
            msg = "No valid documents found to process."
            log_error(msg)
            return JSONResponse(content={"status": "error", "message": msg}, status_code=404)

        add_chunk(conn=conn, data=df)
        log_info(f"Inserted {len(df)} chunks into the database.")

        return JSONResponse(
            content={
                "status": "success",
                "inserted_chunks": len(df),
                "documents": df.to_dict(orient="records"),
            },
            status_code=200,
        )

    except Exception as e:
        log_error(f"Unexpected error in /to_chunks endpoint: {e}")
        return JSONResponse(
            content={"status": "error", "message": "Internal server error"},
            status_code=500,
        )
