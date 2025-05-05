import os
import sys
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info, log_debug, log_warning
    from dbs import add_query_response, fetch_all_rows
    from prompt import UniversityAIPromptBuilder
    from schemes import ChatRoute
    from llm import HuggingFaceLLM
    from db_vector import StartQdrant
    from embedding import EmbeddingService

except Exception as e:
    msg = f"Import Error in: {__file__}, Error: {e}"
    raise ImportError(msg)

chat_route = APIRouter()

def get_llm(request: Request) -> HuggingFaceLLM:
    """Retrieve the LLM instance from the app state."""
    llm = request.app.state.llm
    if not llm:
        log_warning("LLM instance not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM service is not initialized. Please configure the LLM via the /llmsSettings endpoint."
        )
    return llm

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

def format_retrieved_context(retrieved_docs: list[dict]) -> str:
    """Format the retrieved documents into a context string for the prompt."""
    context_parts = []
    for i, doc in enumerate(retrieved_docs, 1):
        context_parts.append(f"Context {i} (Score: {doc['score']:.2f}): {doc['text']}")
    return "\n\n".join(context_parts)

@chat_route.post("/chat", response_class=JSONResponse)
async def chat(
    request: Request,
    use_id: str,
    body: ChatRoute,
    top_k: int = 3,
    score_threshold: float = 0.7,
    llm: HuggingFaceLLM = Depends(get_llm),
    conn = Depends(get_db_conn),
    qdrant: StartQdrant = Depends(get_qdrant_vector_db),
    embedding: EmbeddingService = Depends(get_embedding_model)
) -> JSONResponse:
    """
    Chat endpoint that:
    1. Checks for cached response
    2. Embeds the user query
    3. Retrieves relevant context from vector DB
    4. Generates a response using the LLM
    5. Stores the interaction in the database
    
    Args:
        top_k: Number of relevant chunks to retrieve (default: 3)
        score_threshold: Minimum similarity score for retrieved chunks (default: 0.7)
    """
    # Validate input
    query = body.query.strip()
    if not query:
        log_warning("Empty query received")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )

    # Check cache first
    try:
        cached = fetch_all_rows(
            conn=conn,
            table_name="query_response",
            columns=["response"],
            where_clause=f"user_id = '{use_id}' AND query = '{query}'",
            limit=1
        )
        if cached:
            log_info(f"[CACHE HIT] Found cached response for user {use_id}")
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "status": "success",
                    "response": cached[0]["response"],
                    "cached": True
                }
            )
    except Exception as e:
        log_error(f"Cache check failed: {str(e)}")
        # Continue with normal processing if cache check fails

    try:
        log_debug(f"Processing query from user {use_id}: {query}")
        
        # Step 1: Embed the query
        query_embedding = embedding.embed(text=query)
        
        # Step 2: Retrieve relevant context
        retrieved_docs = qdrant.search_embeddings(
            collection_name="embeddings",
            query_embedding=query_embedding,
            top_k=top_k,
            score_threshold=score_threshold
        )
        
        if not retrieved_docs:
            log_warning("No relevant documents found for query")
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="No relevant information found to answer your query"
            )
        
        # Format the context for the prompt
        context = format_retrieved_context(retrieved_docs)
        log_debug(f"Retrieved context:\n{context}...")

        # Step 3: Build prompt and get LLM response
        try:
            prompt = UniversityAIPromptBuilder().build_prompt(
                context=context,
                user_message=query
            )
            response = llm.response(prompt=prompt)
            log_debug(f"Generated response: {response[:200]}...")
        except Exception as e:
            log_error(f"Response generation failed: {str(e)}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate response"
            )

        # Step 4: Store interaction
        try:
            add_query_response(
                conn=conn,
                query=query,
                response=response,
                user_id=use_id
            )
            log_info(f"Stored interaction for user {use_id}")
        except Exception as e:
            log_error(f"Failed to store interaction: {str(e)}")
            # Continue even if storage fails

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "status": "success",
                "response": response,
                "user_id": use_id,
                "retrieved_docs": len(retrieved_docs),
                "cached": False
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )