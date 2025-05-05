# Standard library
import os
import sys
import subprocess
import time
import uuid

# Third-party libraries
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams


try:
    # Add the root project directory to the system path
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(root_dir)
    from logs import log_debug, log_error, log_info, log_warning
    from helpers import Settings, get_settings
except ImportError as e:
    print(f"[IMPORT ERROR] {e}")
    sys.exit(1)


class StartQdrant:
    """
    StartQdrant is responsible for managing the initialization and connection to a local Qdrant vector database
    using Docker. It ensures:
        - Qdrant container is started with the correct volume and port mapping.
        - Python Qdrant client is initialized and ready.
        - Collections can be created with specified vector configurations.
    
    Logging is handled via custom functions (log_debug, log_error, log_info) to monitor all activity.
    """

    def __init__(self):
        """
        Constructor for the StartQdrant class.

        It performs the following:
        - Loads application settings from a config class.
        - Prepares and runs the Qdrant Docker container using those settings.
        - Initializes the Qdrant Python client for future communication.
        """
        try:
            self.app_setting: Settings = get_settings()

            self.docker_command = [
                "docker", "run", "-d",  # Run in detached mode (background)
                "-p", f"{self.app_setting.PORT}:{self.app_setting.PORT}",
                "-v", f"{self.app_setting.VECTOR_DB}:/qdrant/storage",
                "qdrant/qdrant"
            ]

            log_info("[QDRANT INIT] Starting Qdrant setup...")
            self.__run_docker_qdrant()
            self.__init_qdrant_client()
        except Exception as e:
            log_error(f"[QDRANT INIT] Failed to initialize Qdrant: {e}")
            raise

    def __run_docker_qdrant(self) -> None:
        """
        Internal method that starts the Qdrant Docker container.

        Steps:
        - Executes Docker command with volume mapping and port binding.
        - Waits a few seconds for Qdrant to initialize.
        - Logs all stdout and stderr messages for monitoring.

        Raises:
            Exception: If Docker fails to run or output returns errors.
        """
        try:
            log_info("[QDRANT DOCKER] Running container...")
            process = subprocess.Popen(
                self.docker_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if stdout:
                log_debug(f"[QDRANT DOCKER] Output: {stdout.decode().strip()}")
            if stderr:
                log_error(f"[QDRANT DOCKER] Error: {stderr.decode().strip()}")

            log_info("[QDRANT DOCKER] Container is starting up. Waiting for initialization...")
            time.sleep(6)
        except Exception as e:
            log_error(f"[QDRANT DOCKER] Failed to run Docker container: {e}")
            raise

    def __init_qdrant_client(self) -> None:
        """
        Internal method that initializes the QdrantClient using host and port from settings.

        This is used to interact with Qdrant from Python after Docker starts.

        Raises:
            Exception: If connection to Qdrant fails.
        """
        try:
            self.client = QdrantClient(
                host=self.app_setting.HOST,
                port=self.app_setting.PORT
            )
            log_info(f"[QDRANT CLIENT] Connected to Qdrant at {self.app_setting.HOST}:{self.app_setting.PORT}")
        except Exception as e:
            log_error(f"[QDRANT CLIENT] Failed to initialize client: {e}")
            raise

    def create_collection(self, collection_name: str, vector_size: int = 384) -> None:
        """
        Public method to create a collection in Qdrant with given name and vector configuration.

        Args:
            collection_name (str): The name of the Qdrant collection (e.g. 'chunks_metadata').
            vector_size (int): The size of the embedding vectors (default is 384 for MiniLM-type models).

        Raises:
            Exception: If the collection fails to create or if communication with Qdrant fails.
        """
        try:
            vectors_config = VectorParams(size=vector_size, distance=Distance.COSINE)
            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=vectors_config
            )
            log_info(f"[QDRANT COLLECTION] '{collection_name}' created with vector size {vector_size}.")
        except Exception as e:
            log_error(f"[QDRANT COLLECTION] Failed to create collection '{collection_name}': {e}")
            raise
    def insert_embedding(
        self,
        collection_name: str,
        embedding: list[float] | np.ndarray,
        id_: str | int = None,
        payload: dict = None
    ) -> None:
        """
        Inserts a single embedding into the specified Qdrant collection.
    
        Args:
            collection_name (str): Target Qdrant collection name.
            embedding (list or np.ndarray): Vector embedding to insert.
            id_ (str|int): Unique ID for the vector. If None, a UUID will be generated.
            payload (dict): Optional metadata to store alongside the vector.
        """
        try:
            if id_ is None:
                id_ = str(uuid.uuid4())
    
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
    
            point = PointStruct(id=id_, vector=embedding, payload=payload or {})
            self.client.upsert(collection_name=collection_name, points=[point])
            log_info(f"[QDRANT UPSERT] Inserted point ID {id_} into '{collection_name}'.")
        except Exception as e:
            log_error(f"[QDRANT UPSERT] Failed to insert point: {e}")
            raise
    
    def search_embeddings(
        self,
        collection_name: str,
        query_embedding: list[float] | np.ndarray,
        top_k: int = 5,
        score_threshold: float = 0.5
    ) -> list[dict]:
        """
        Search for similar embeddings in the collection and return top k results with text chunks.
        
        Args:
            collection_name (str): Name of the Qdrant collection to search
            query_embedding (list[float] | np.ndarray): The embedding vector to search with
            top_k (int): Number of top results to return
            score_threshold (float): Minimum similarity score to consider (0.0 to 1.0)
        
        Returns:
            list[dict]: List of results containing:
                - text: The text chunk from payload
                - score: Similarity score
                - id: The point ID
        
        Raises:
            Exception: If search fails or collection doesn't exist
        """
        try:
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
            
            # Perform the search
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )
            
            # Format the results
            results = []
            for hit in search_results:
                if hit.payload and "text" in hit.payload:
                    results.append({
                        "text": hit.payload["text"],
                        "score": hit.score,
                        "id": hit.id
                    })
                else:
                    log_warning(f"Search result missing 'text' in payload: {hit}")
            
            log_info(f"[QDRANT SEARCH] Found {len(results)} results (requested {top_k})")
            return results
            
        except Exception as e:
            log_error(f"[QDRANT SEARCH] Failed to search embeddings: {e}")
            raise

if __name__ == "__main__":
    try:
        # Initialize and set up Qdrant
        qdrant = StartQdrant()
        qdrant.create_collection("embeddings")

        # Create a normalized test embedding (size 384)
        embedding = np.array([float(i) for i in range(384)], dtype=np.float32)
        embedding = embedding / np.linalg.norm(embedding)

        # Insert test embedding
        qdrant.insert_embedding(
            "embeddings",
            embedding=embedding,
            id_=1,
            payload={"note": "Test embedding"}
        )

    except Exception as main_err:
        log_error(f"[MAIN] Unrecoverable error during Qdrant setup: {main_err}")

