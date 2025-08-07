# finetuner/main.py

import os
import threading
from flask import Flask, jsonify, request, render_template, send_from_directory
from pyngrok import ngrok
from flask_cors import CORS
from .config import Config
from .data_loader import DataLoader
from .model_manager import ModelManager
from .trainer import Trainer

# --- App Initialization ---
# More robust path definition for static files and templates
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

CORS(app)
# --- Global variable to track training status ---
training_status = {"running": False, "log": "Awaiting job..."}

# --- API Endpoints ---
# All API routes are now prefixed with /api/ to keep them separate from the frontend.

@app.route('/api/config', methods=['GET'])
def get_config():
    """NEW: Provides the frontend with necessary configuration, like the model list."""
    return jsonify({
        'supported_models': Config.SUPPORTED_MODELS
    })

@app.route('/api/finetune', methods=['POST'])
def finetune():
    """Starts the fine-tuning process in a background thread."""
    global training_status
    if training_status['running']:
        return jsonify({'status': 'error', 'message': 'A training job is already in progress.'}), 400

    data = request.json
    training_status['running'] = True
    training_status['log'] = "Received job request. Starting..."

    thread = threading.Thread(target=run_finetuning_thread, args=(data,))
    thread.start()

    return jsonify({'status': 'success', 'message': 'Fine-tuning process started.'})

@app.route('/api/status')
def status():
    """Provides real-time status updates for the training process."""
    return jsonify(training_status)


# --- Frontend Serving Routes ---
# These routes are responsible for serving the compiled React application.

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """NEW: Serves files from the static/assets folder to fix 404 errors."""
    return send_from_directory(os.path.join(app.static_folder, 'assets'), filename)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """CHANGED: This is now the 'catch-all' route that serves the React app."""
    return render_template('index.html')


# --- The rest of your fine-tuning logic and app runners remain the same ---

def run_finetuning_thread(data):
    """The actual fine-tuning logic that will run in a separate thread."""
    global training_status
    try:
        dataset_path = data.get('dataset_path')
        model_name = data.get('model_name')
        hyperparameters = data.get('hyperparameters', Config.DEFAULT_HYPERPARAMETERS)
        output_dir = './fine_tuned_model'

        training_status['log'] = f"Starting fine-tuning for model: {model_name}..."
        
        # 1. Load Data
        training_status['log'] += "\n> Loading dataset..."
        data_loader = DataLoader(dataset_path)
        dataset = data_loader.load()
        if not dataset:
            raise ValueError("Failed to load dataset.")

        # 2. Load Model
        training_status['log'] += "\n> Loading model (this may take a while)..."
        model_manager = ModelManager(model_name)
        model, tokenizer = model_manager.load()
        if not model or not tokenizer:
            raise ValueError("Failed to load model. Check logs for authentication issues.")

        # 3. Train Model
        training_status['log'] += "\n> Starting training process..."
        trainer = Trainer(model, tokenizer, dataset, hyperparameters)
        saved_path = trainer.train(output_dir)

        training_status['log'] += f"\n\nTraining complete! Model saved at: {os.path.abspath(saved_path)}"

    except Exception as e:
        training_status['log'] += f"\n\n--- ERROR ---\n{str(e)}"
    finally:
        training_status['running'] = False


def run_app():
    """Runs the Flask application for standard local development."""
    app.run(host='0.0.0.0', port=5001, debug=False) # Note: debug=False is better for this setup

def run_app_with_ngrok():
    """Runs the Flask application and exposes it to the web using ngrok."""
    port = 5001
    ngrok.kill()
    public_url = ngrok.connect(port)
    print(f"--- Public URL: {public_url} ---")
    app.run(port=port)

if __name__ == '__main__':
    run_app()
