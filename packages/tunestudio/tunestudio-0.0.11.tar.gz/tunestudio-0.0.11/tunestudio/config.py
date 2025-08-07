class Config:
    """
    Configuration class to store the default settings for the hyperparamters and the supported models for finetuning
    """
    DEFAULT_HYPERPARAMETERS = {
        'learning_rate': 2e-5,
        'batch_size': 16,
        'num_epochs': 3,
        'weight_decay': 0.01,
    }

    
    SUPPORTED_MODELS = [
        # --- Llama 3.1 Family ---
        'meta-llama/Llama-3.1-8B',
        'meta-llama/Llama-3.1-8B-Instruct',
        'meta-llama/Llama-3.1-70B',
        'meta-llama/Llama-3.1-70B-Instruct',
        'meta-llama/Llama-3.1-405B',
        'meta-llama/Llama-3.1-405B-Instruct',

        # --- Gemma Family ---
        'google/gemma-2b',
        'google/gemma-2b-it',
        'google/gemma-7b',
        'google/gemma-7b-it',
        'google/gemma-2-9b',
        'google/gemma-2-9b-it',
        'google/gemma-2-27b',
        'google/gemma-2-27b-it',

        # --- Phi-3 Family ---
        'microsoft/Phi-3-mini-4k-instruct',
        'microsoft/Phi-3-mini-128k-instruct',
        'microsoft/Phi-3-small-8k-instruct',
        'microsoft/Phi-3-small-128k-instruct',
        'microsoft/Phi-3-medium-4k-instruct',
        'microsoft/Phi-3-medium-128k-instruct',
        'microsoft/Phi-3-vision-128k-instruct',

        # --- Mistral Family ---
        'mistralai/Mistral-7B-v0.1',
        'mistralai/Mistral-7B-Instruct-v0.1',
        'mistralai/Mistral-7B-v0.2',
        'mistralai/Mistral-7B-Instruct-v0.2',
        'mistralai/Mixtral-8x7B-v0.1',
        'mistralai/Mixtral-8x7B-Instruct-v0.1',
        'mistralai/Mixtral-8x22B-v0.1',
        'mistralai/Mixtral-8x22B-Instruct-v0.1',

        # --- Qwen2 Family ---
        'Qwen/Qwen2-0.5B',
        'Qwen/Qwen2-0.5B-Instruct',
        'Qwen/Qwen2-1.5B',
        'Qwen/Qwen2-1.5B-Instruct',
        'Qwen/Qwen2-7B',
        'Qwen/Qwen2-7B-Instruct',
        'Qwen/Qwen2-72B',
        'Qwen/Qwen2-72B-Instruct',

        # --- BERT Family (for classification/feature extraction) ---
        'bert-base-uncased',
        'bert-large-uncased',
        'distilbert-base-uncased',
        'roberta-base',
        'roberta-large',
        'albert-base-v2',
        'albert-large-v2',

        # --- Other Popular Models ---
        'EleutherAI/gpt-neo-125M',
        'EleutherAI/gpt-neo-1.3B',
        'EleutherAI/gpt-j-6B',
        'bigscience/bloom-560m',
        'bigscience/bloom-1b7',
        'tiiuae/falcon-7b',
        'tiiuae/falcon-7b-instruct',
        'google-bert/bert-base-multilingual-cased'
    ]