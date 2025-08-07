# finetuner/trainer.py

from transformers import Trainer as HfTrainer, TrainingArguments
from .config import Config
import os

class Trainer:
    """
    Manages the fine-tuning process of a model on a given dataset.
    """
    def __init__(self, model, tokenizer, dataset, hyperparameters=None):
        """
        Initializes the Trainer.

        Args:
            model: The pre-trained model to be fine-tuned.
            tokenizer: The tokenizer associated with the model.
            dataset: The dataset (from DataLoader) to train on. Should be a Hugging Face Dataset object.
            hyperparameters (dict, optional): A dictionary of training hyperparameters. 
                                              Defaults to Config.DEFAULT_HYPERPARAMETERS.
        """
        self.model = model
        self.tokenizer = tokenizer
        self.dataset = dataset
        self.hyperparameters = hyperparameters if hyperparameters is not None else Config.DEFAULT_HYPERPARAMETERS

        # For simplicity, we'll assume the dataset has 'train' and optionally 'test' splits.
        # A more robust implementation would handle split names dynamically.
        self.train_dataset = self.dataset.get('train')
        self.eval_dataset = self.dataset.get('test') # Can be None

    def _preprocess_data(self, examples):
        """A simple preprocessing function to tokenize the text."""
        # This assumes the dataset has a 'text' column.
        # This function will need to be made more flexible for different dataset structures.
        return self.tokenizer(examples['text'], truncation=True, padding='max_length', max_length=512)

    def train(self, output_dir: str = './results'):
        """
        Executes the fine-tuning process.

        Args:
            output_dir (str): The directory where the fine-tuned model and training outputs will be saved.
        """
        if self.train_dataset is None:
            raise ValueError("Training dataset not found. Please ensure your dataset has a 'train' split.")

        print("Preprocessing dataset...")
        # Note: For Causal LM fine-tuning, the preprocessing is more complex.
        # This is a simplified version for demonstration. A real-world tool would need
        # a more advanced data preparation step depending on the task (e.g., text classification vs. generation).
        tokenized_train_dataset = self.train_dataset.map(self._preprocess_data, batched=True)
        tokenized_eval_dataset = self.eval_dataset.map(self._preprocess_data, batched=True) if self.eval_dataset else None

        # Set up training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=self.hyperparameters.get('num_epochs', 3),
            per_device_train_batch_size=self.hyperparameters.get('batch_size', 16),
            learning_rate=self.hyperparameters.get('learning_rate', 2e-5),
            weight_decay=self.hyperparameters.get('weight_decay', 0.01),
            logging_dir=os.path.join(output_dir, 'logs'),
            logging_steps=10,
            evaluation_strategy="epoch" if tokenized_eval_dataset else "no",
            save_strategy="epoch",
            load_best_model_at_end=True if tokenized_eval_dataset else False,
        )

        # Initialize the Hugging Face Trainer
        hf_trainer = HfTrainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_train_dataset,
            eval_dataset=tokenized_eval_dataset,
            tokenizer=self.tokenizer,
        )

        print("Starting fine-tuning...")
        hf_trainer.train()
        print("Fine-tuning complete.")

        # Save the fine-tuned model
        self.save_model(output_dir)
        return output_dir

    def save_model(self, path: str):
        """Saves the fine-tuned model and tokenizer to the specified path."""
        print(f"Saving model to {path}...")
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        print("Model saved successfully.")

