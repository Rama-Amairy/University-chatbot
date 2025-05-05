from pydantic import BaseModel
from typing import Optional

class LLMsSettings(BaseModel):
    model_name: Optional[str] 
    max_new_tokens: int
    do_sample: bool 
    temperature: float 
    top_p: float 
    top_k: int 
    trust_remote_code: bool
    quantization: bool 
    quantization_type: str 


# Default model config as fallback
llm_config = {
    "model_name": None,
    "max_new_tokens": 512,
    "do_sample": True,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50,
    "trust_remote_code": False,
    "quantization": False,
    "quantization_type": "none"
}