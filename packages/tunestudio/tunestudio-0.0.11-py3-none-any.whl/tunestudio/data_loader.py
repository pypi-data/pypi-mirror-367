from datasets import load_dataset
import pandas as pd
import os

class DataLoader:
    """
    Handles loading datasets from various sources and formats.
    It can load data from local files (CSV, JSON) or from the Hugging Face Hub.
    """
    def __init__(self, dataset_path: str):
        """
        Initializes the DataLoader.

        Args:
            dataset_path (str): The path to the local file or the name of the dataset on the Hugging Face Hub.
        """
        self.dataset_path = dataset_path
        self.dataset = None

    def load(self):
        """
        Loads the dataset based on the provided path.
        Detects if it's a local file path or a Hugging Face Hub dataset name.
        """
        try:
            # Check if the path is a local file
            if os.path.exists(self.dataset_path):
                # Infer file type from extension
                file_type = self.dataset_path.split('.')[-1]
                if file_type not in ['csv', 'json']:
                    raise ValueError(f"Unsupported file type: '{file_type}'. Please use CSV or JSON.")
                
                print(f"Loading local {file_type} file from: {self.dataset_path}")
                self.dataset = load_dataset(file_type, data_files=self.dataset_path)

            # Otherwise, assume it's a dataset from the Hugging Face Hub
            else:
                print(f"Loading dataset from Hugging Face Hub: {self.dataset_path}")
                self.dataset = load_dataset(self.dataset_path)

            print("Dataset loaded successfully.")
            print("Dataset features:", self.dataset)
            return self.dataset

        except Exception as e:
            print(f"Error loading dataset: {e}")
            return None

    def get_dataset(self):
        """
        Returns the loaded dataset object.
        """
        return self.dataset

# Example of how to use this class (for testing purposes)
if __name__ == '__main__':
    # --- Test with a local CSV file ---
    # Create a dummy CSV for testing
    print("--- Testing with a local CSV file ---")
    dummy_data = {'text': ['This is the first sentence.', 'This is a second sentence.'], 'label': [0, 1]}
    dummy_df = pd.DataFrame(dummy_data)
    dummy_csv_path = 'dummy_dataset.csv'
    dummy_df.to_csv(dummy_csv_path, index=False)

    # Load the local CSV
    local_loader = DataLoader(dataset_path=dummy_csv_path)
    local_dataset = local_loader.load()
    if local_dataset:
        print("Local CSV loaded successfully!")
        print(local_dataset['train'][0]) # Print the first example
    
    # Clean up the dummy file
    os.remove(dummy_csv_path)
    
    
    print("\n--- Testing with a Hugging Face Hub dataset ---")
    hub_loader = DataLoader(dataset_path='glue') 
    hub_dataset = hub_loader.load()
    if hub_dataset:
        print("Hub dataset loaded successfully!")
        print(hub_dataset['train'][0]) 
