from pydantic import BaseModel
from typing import Optional

class ChatRoute(BaseModel):
    query: str 