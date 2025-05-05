from abc import ABC, abstractmethod

class ILLMsGenerators(ABC):
    """
    Abstract base class for LLM generators.
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
                 quantization_type: str = "8bit"  # Options: "8bit", "4bit"
    ) -> None:
        """
        Initializes the LLM generator with given parameters.

        Args:
            model_name (str): The name of the model to use.
            max_new_tokens (int): Maximum length of the generated text.
            do_sample (bool, optional): Whether to use sampling. Default is True.
            temperature (float, optional): Sampling temperature. Default is 0.5.
            top_p (float, optional): Cumulative probability for top-p sampling. Default is 0.95.
            top_k (int, optional): Number of highest probability tokens to keep for sampling. Default is 50.
            trust_remote_code (bool, optional): Whether to trust remote code execution. Default is False.
            quantization (bool, optional): Whether to load the model with quantization. Default is False.
            quantization_type (str, optional): Type of quantization ("8bit", "4bit"). Default is "8bit".
        """
        pass

    @abstractmethod
    def initialize_llm(self):
        """
        
        
        """
        pass 

    @abstractmethod
    def response(self, prompt: str) -> str:
        """
        Generates a response from the LLM based on the provided prompt.

        Args:
            prompt (str): The input text to generate a response for.

        Returns:
            str: The generated response.
        """
        pass
