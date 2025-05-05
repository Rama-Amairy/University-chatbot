import os
import sys
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

# Add main directory to path
MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(MAIN_DIR)

from src.logs import log_info, log_error
from routes import (
    hello_routes,
    upload_route,
    to_chunks_route,
    chunks_embedding_route,
    chat_route,
    llm_setting_route
)
from dbs import (
    get_sqlite_engine,
    init_chunks_table,
    init_query_response_table
)
from db_vector import StartQdrant
from embedding import EmbeddingService
from llm import HuggingFaceLLM
from schemes import llm_config

app = FastAPI(
    title="University-AI-Assistant",
    description="AI Assistant for University Applications",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize application state"""
    try:
        log_info("[STARTUP] Initializing application components...")
        
        # Initialize vector database
        app.state.qdrant = StartQdrant()
        app.state.embedded = EmbeddingService()
        app.state.qdrant.create_collection("embeddings")
        
        # Initialize SQLite database
        app.state.conn = get_sqlite_engine()
        init_chunks_table(conn=app.state.conn)
        init_query_response_table(conn=app.state.conn)
        
        # Initialize LLM with default config
        app.state.llm = HuggingFaceLLM(**llm_config)
        log_info("[STARTUP] LLM initialized with default configuration")
        
        log_info("[STARTUP] Application components initialized successfully.")
    except Exception as e:
        log_error(f"[STARTUP ERROR] Failed to initialize application: {str(e)}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    try:
        log_info("[SHUTDOWN] Shutting down application...")
        
        # Close database connections
        if hasattr(app.state, 'conn'):
            app.state.conn.close()
            log_info("[SHUTDOWN] SQLite connection closed.")
        
        # Clean up LLM resources
        if hasattr(app.state, 'llm'):
            del app.state.llm
            log_info("[SHUTDOWN] LLM resources released.")
            
        log_info("[SHUTDOWN] Application shutdown completed.")
    except Exception as e:
        log_error(f"[SHUTDOWN ERROR] Error during shutdown: {str(e)}", exc_info=True)

# Include all routers
app.include_router(hello_routes, prefix="/hello", tags=["Hello World"])
app.include_router(upload_route, prefix="/upload", tags=["Document Upload"])
app.include_router(to_chunks_route, prefix="/toChunks", tags=["Document Processing"])
app.include_router(chunks_embedding_route, prefix="/chunksEmbedding", tags=["Embedding Generation"])
app.include_router(chat_route, prefix="/Chatbot", tags=["Chatbot Interaction"])
app.include_router(llm_setting_route, prefix="/llmsSettings", tags=["LLM Configuration"])