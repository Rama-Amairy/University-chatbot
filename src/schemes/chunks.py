from pydantic import BaseModel
from typing import Optional

class ChunkRequest(BaseModel):
    file_path: Optional[str] = None 
    do_reset: int = 0