import os
import sys
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
import sqlite3
from src.logs.logger import log_warning

# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from dbs import fetch_all_rows
    from logs import log_error, log_info
    from embedding import EmbeddingService
    from db_vector import StartQdrant
except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")

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

def get_qdrant_vector_db(request: Request) -> StartQdrant:
    """Retrieve the Qdrant vector database connection from the app state."""
    qdrant = request.app.state.qdrant
    if not qdrant:
        log_warning("Qdrant vector database connection not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vector database service is not available."
        )
    return qdrant

def get_embedding_model(request: Request) -> EmbeddingService:
    """Retrieve the embedding model instance from the app state."""
    embedding = request.app.state.embedded
    if not embedding:
        log_warning("Embedding model instance not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding model service is not available."
        )
    return embedding

chunks_embedding_route = APIRouter()

@chunks_embedding_route.post("/chunks_to_embedding", response_class=JSONResponse)
async def chunks_to_embedding(request: Request,
                              conn: sqlite3.Connection = Depends(get_db_conn),
                              qdrant: StartQdrant = Depends(get_qdrant_vector_db),
                              embed: EmbeddingService = Depends(get_embedding_model)):
    """
    Convert text chunks to embedding and store them in the database.
    """
    try:
        # Pull chunks from the database
        chunks = fetch_all_rows(conn=conn, table_name="chunks", columns=["text", "id"])
        if not chunks:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No chunks found in the database.")
        
        log_info(f"Pulled {len(chunks)} chunk(s) from the database.")
        for chunk in chunks:
            # Convert chunks to embedding
            embedding = embed.embed(text=chunk["text"])

            # Store the embedding in the database
            qdrant.insert_embedding(
                "embeddings",
                embedding=embedding,
                id_=chunk["id"],
                payload={"text": chunk["text"]}
            )

        return JSONResponse(content={"status": "success"}, status_code=HTTP_200_OK)

    except HTTPException as http_exc:
        # Re-raise FastAPI errors
        log_error(f"HTTPException in chunks_to_embedding: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        # Handle unexpected errors
        log_error(f"Unexpected error in chunks_to_embedding: {e}")
        return JSONResponse(content={"status": "error", "detail": str(e)}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)