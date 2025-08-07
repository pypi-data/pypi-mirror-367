# finetuner/model_manager.py

from transformers import AutoTokenizer, AutoModelForCausalLM
from .config import Config
import torch
from huggingface_hub import HfApi, HfFolder

class ModelManager:
    """
    Handles the loading of pre-trained models and their tokenizers from the Hugging Face Hub.
    Includes a check for gated models to guide user authentication.
    """
    def __init__(self, model_name: str):
        """
        Initializes the ModelManager.

        Args:
            model_name (str): The name of the model to load, as listed in Config.SUPPORTED_MODELS.
        """
        if model_name not in Config.SUPPORTED_MODELS:
            raise ValueError(f"Model '{model_name}' is not supported. Please choose from the list in config.py.")
        
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")

    def _is_gated_model(self) -> bool:
        """
        A simple check to see if the model name suggests it might be gated.
        Models from 'meta-llama', 'google/gemma', etc., typically require authentication.
        """
        gated_prefixes = ['meta-llama', 'google/gemma', 'microsoft/Phi-3']
        return any(self.model_name.startswith(prefix) for prefix in gated_prefixes)

    def _check_hf_login(self):
        """Checks if a Hugging Face token is available."""
        return HfFolder.get_token() is not None

    def load(self):
        """
        Loads the pre-trained model and tokenizer from the Hugging Face Hub.
        """
        try:
            # Check for authentication if the model is likely gated
            if self._is_gated_model() and not self._check_hf_login():
                print(f"--- ATTENTION ---")
                print(f"Model '{self.model_name}' is a gated model and requires you to be logged into Hugging Face.")
                print("Please run the following in your terminal or a notebook cell first:")
                print("1. `pip install huggingface_hub`")
                print("2. `huggingface-cli login` (and enter your token)")
                print("-------------------")
                raise PermissionError("Hugging Face login required for this model.")

            print(f"Loading model and tokenizer for '{self.model_name}'...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map=self.device
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.model.config.pad_token_id = self.model.config.eos_token_id
            
            print(f"Model '{self.model_name}' loaded successfully on {self.device}.")
            return self.model, self.tokenizer

        except PermissionError as e:
            # Catch the specific permission error we raised.
            print(f"Halting execution: {e}")
            return None, None
        except Exception as e:
            print(f"An unexpected error occurred while loading model '{self.model_name}': {e}")
            return None, None

    def get_model_and_tokenizer(self):
        """Returns the loaded model and tokenizer."""
        return self.model, self.tokenizer
