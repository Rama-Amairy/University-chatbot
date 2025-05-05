import os
import sys
from abc import ABC, abstractmethod
from typing import Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import BitsAndBytesConfig
from huggingface_hub import login

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)
    from logs import log_error, log_info, log_debug, log_warning
    from helpers import get_settings, Settings
    from llm import ILLMsGenerators
except ImportError as ie:
    raise ImportError(f"ImportError in HuggingFace wrapper: {ie}")

class HuggingFaceLLM(ILLMsGenerators):
    """
    Concrete implementation of ILLMsGenerators for HuggingFace models with comprehensive
    error handling and logging.
    """
    
    def __init__(self,
                 model_name: str,
                 max_new_tokens: int,
                 do_sample: bool = True,
                 temperature: float = 0.5,
                 top_p: float = 0.95,
                 top_k: int = 50,
                 trust_remote_code: bool = False,
                 quantization: bool = False,
                 quantization_type: str = "8bit",
                 device_map: Optional[str] = "auto",
        ) -> None:
        """
        Initializes the HuggingFace LLM generator with enhanced error handling.
        """
        try:
            self.settings: Settings = get_settings()

            self.model_name = model_name or self.settings.HUGGINGFACE_MODEL_NAME
            self.max_new_tokens = max_new_tokens
            self.do_sample = do_sample
            self.temperature = temperature
            self.top_p = top_p
            self.top_k = top_k
            self.trust_remote_code = trust_remote_code
            self.quantization = quantization
            self.quantization_type = quantization_type
            self.device_map = device_map
            
            self.model = None
            self.tokenizer = None

            log_info(f"Initializing HuggingFace LLM with model: {model_name}")

            log_debug("Loging to HuggingFace hub")
            log_debug(f"Generation params - temp: {temperature}, top_p: {top_p}, top_k: {top_k}")
            
            self.initialize_llm()
            log_info("HuggingFace LLM initialized successfully")
            
        except Exception as e:
            log_error(f"Failed to initialize HuggingFaceLLM: {str(e)}")
            raise RuntimeError(f"HuggingFaceLLM initialization failed: {e}") from e
    
    def initialize_llm(self):
        """
        Initializes the HuggingFace model and tokenizer with comprehensive error handling.
        """
        # Login to Hugginfce use Tokeinzer
        login(self.settings.HUGGINGFACE_TOKIENS)

        try:
            # Configure quantization if enabled
            quantization_config = None
            if self.quantization:
                log_info(f"Configuring {self.quantization_type} quantization")
                try:
                    if self.quantization_type == "8bit":
                        quantization_config = BitsAndBytesConfig(load_in_8bit=True)
                    elif self.quantization_type == "4bit":
                        quantization_config = BitsAndBytesConfig(
                            load_in_4bit=True,
                            bnb_4bit_compute_dtype=torch.float16,
                            bnb_4bit_quant_type="nf4",
                            bnb_4bit_use_double_quant=True
                        )
                    else:
                        log_warning(f"Unsupported quantization type: {self.quantization_type}")
                        raise ValueError(f"Unsupported quantization type: {self.quantization_type}")
                except Exception as e:
                    log_error(f"Quantization configuration failed: {e}")
                    raise

            # Load tokenizer
            log_debug(f"Loading tokenizer for {self.model_name}")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    trust_remote_code=self.trust_remote_code
                )
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                    log_debug("Set pad_token to eos_token")
            except Exception as e:
                log_error(f"Tokenizer loading failed: {e}")
                raise

            # Load model with optional quantization
            log_debug(f"Loading model {self.model_name}")
            try:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    device_map=self.device_map,
                    quantization_config=quantization_config,
                    trust_remote_code=self.trust_remote_code
                )
                
                # Set model to eval mode for inference
                self.model.eval()
                log_debug("Model loaded and set to evaluation mode")
                
            except Exception as e:
                log_error(f"Model loading failed: {e}")
                raise
                
        except Exception as e:
            log_error(f"LLM initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize LLM: {e}") from e
    
    def response(self, prompt: str) -> str:
        """
        Generates a response with comprehensive error handling and logging.
        
        Args:
            prompt (str): The input text to generate a response for.
            
        Returns:
            str: The generated response.
            
        Raises:
            RuntimeError: If generation fails
        """
        try:
            if not prompt or not isinstance(prompt, str):
                log_warning("Empty or invalid prompt received")
                raise ValueError("Prompt must be a non-empty string")
            
            log_debug(f"Generating response for prompt (length: {len(prompt)})")
            
            # Tokenize the input prompt
            try:
                input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.model.device)
                log_debug("Prompt tokenized successfully")
            except Exception as e:
                log_error(f"Tokenization failed: {e}")
                raise

            # Generate output
            try:
                with torch.no_grad():
                    output = self.model.generate(
                        input_ids,
                        max_new_tokens=self.max_new_tokens,
                        do_sample=self.do_sample,
                        temperature=self.temperature,
                        top_p=self.top_p,
                        top_k=self.top_k,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                log_debug("Generation completed successfully")
            except Exception as e:
                log_error(f"Generation failed: {e}")
                raise

            # Decode and return the generated text
            try:
                generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
                log_debug(f"Generated response (length: {len(generated_text)})")
                return generated_text
            except Exception as e:
                log_error(f"Response decoding failed: {e}")
                raise
                
        except Exception as e:
            log_error(f"Failed to generate response: {e}")
            raise RuntimeError(f"Response generation failed: {e}") from e
    
    def __str__(self) -> str:
        return f"HuggingFaceLLM(model={self.model_name}, quantized={self.quantization})"

    def __del__(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'model') and self.model is not None:
                del self.model
                log_debug("Model cleared from memory")
            if hasattr(self, 'tokenizer') and self.tokenizer is not None:
                del self.tokenizer
                log_debug("Tokenizer cleared from memory")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                log_debug("CUDA cache cleared")
        except Exception as e:
            log_warning(f"Cleanup failed: {e}")



if __name__ == "__main__":
    try:
        llm = HuggingFaceLLM(
            model_name="meta-llama/Llama-3.2-1B",
            max_new_tokens=200,
            temperature=0.7,
        )
        
        response = llm.response("Explain quantum computing simply")
        print(response)
        
    except Exception as e:
        log_error(f"Application error: {e}")
        # Handle error or re-raise