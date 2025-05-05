from fastapi import Request, HTTPException
from sqlite3 import Connection
from llm import HuggingFaceLLM

def get_dependencies(request: Request) -> tuple[HuggingFaceLLM, Connection]:
    llm = getattr(request.app, "llm", None)
    conn = getattr(request.app, "conn", None)

    if llm is None:
        raise HTTPException(status_code=500, detail="LLM not initialized. Please call /llmsSettings/llmConfiguration first.")

    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection not available.")

    return llm, conn
