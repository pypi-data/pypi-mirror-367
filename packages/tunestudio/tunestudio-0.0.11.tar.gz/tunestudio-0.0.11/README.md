# TuneStudio - No-Code LLM Fine-Tuning Platform

[![PyPI version](https://badge.fury.io/py/tunestudio.svg)](https://pypi.org/project/tunestudio/0.0.11/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A beautiful, modern web interface for fine-tuning large language models without writing code. Built with Flask backend and React frontend, designed to run locally or in cloud environments like Google Colab and Kaggle.

![TuneStudio Demo](https://via.placeholder.com/800x400/1a1a1a/ffffff?text=TuneStudio+Demo)

## ✨ Features

- **🚀 No-Code Interface**: Beautiful, modern web UI for configuring and monitoring fine-tuning jobs
- **🤖 50+ Pre-supported Models**: Including Llama 3.1, Gemma, Phi-3, Mistral, Qwen2, BERT, and more
- **⚡ Real-time Logging**: Live progress monitoring with automatic log updates
- **🔧 Flexible Configuration**: Easy hyperparameter tuning with sensible defaults
- **☁️ Cloud-Ready**: Works seamlessly in Colab/Kaggle with ngrok integration
- **💻 Local Execution**: Uses your local GPU/CPU resources - no data sent to external services
- **📊 Professional UI**: Dark theme, responsive design, smooth animations
- **🔄 Auto-scrolling Logs**: Real-time log updates with automatic scroll-to-bottom

## 🚀 Quick Start

### Installation

pip install tunestudio

text

### Local Usage

Start the web interface
tunestudio

text

Then open your browser to `http://localhost:5001`

### Google Colab / Kaggle Usage

In a Colab/Kaggle notebook cell
import tunestudio
tunestudio.main.run_app_with_ngrok()

text

Or use the command line:
tunestudio-colab

text

## 📖 Usage Guide

### 1. Dataset Preparation
- **Local CSV File**: Place your training data in a CSV file with a `text` column
- **Hugging Face Dataset**: Use any dataset name from Hugging Face Hub (e.g., `imdb`, `rotten_tomatoes`)

Example CSV format:
text
"This is a positive example for training."
"This is another training sample."
"Fine-tuning is made easy with TuneStudio."

text

### 2. Model Selection
Choose from 50+ supported models including:
- **Llama 3.1**: `meta-llama/Llama-3.1-8B`, `meta-llama/Llama-3.1-8B-Instruct`
- **Gemma**: `google/gemma-2b`, `google/gemma-7b`, `google/gemma-2-9b`
- **Phi-3**: `microsoft/Phi-3-mini-4k-instruct`, `microsoft/Phi-3-small-8k-instruct`
- **Mistral**: `mistralai/Mistral-7B-v0.1`, `mistralai/Mixtral-8x7B-v0.1`
- **And many more...**

### 3. Configuration
1. Enter your dataset path or Hub name
2. Select a model from the dropdown
3. Adjust hyperparameters (optional):
   - Learning Rate (default: 2e-5)
   - Batch Size (default: 16)
   - Epochs (default: 3)

### 4. Training
1. Click "Start Fine-Tuning"
2. Monitor real-time progress in the live log panel
3. Your fine-tuned model will be saved to `./fine_tuned_model/`

## 🛠️ Supported Models

### Large Language Models
- **Llama 3.1**: All variants (8B, 70B, 405B, Instruct versions)
- **Gemma**: Google's efficient models (2B, 7B, 9B, 27B variants)
- **Phi-3**: Microsoft's small but powerful models (mini, small, medium)
- **Mistral**: Including Mixtral MoE variants (7B, 8x7B, 8x22B)
- **Qwen2**: Alibaba's multilingual models (0.5B to 72B)

### Encoder Models (for classification)
- **BERT Family**: `bert-base-uncased`, `bert-large-uncased`, `distilbert-base-uncased`
- **RoBERTa**: `roberta-base`, `roberta-large`
- **ALBERT**: `albert-base-v2`, `albert-large-v2`

### Other Popular Models
- **GPT**: `EleutherAI/gpt-neo-125M`, `EleutherAI/gpt-j-6B`
- **BLOOM**: `bigscience/bloom-560m`, `bigscience/bloom-1b7`
- **Falcon**: `tiiuae/falcon-7b`, `tiiuae/falcon-7b-instruct`

## 🔧 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (16GB+ recommended for larger models)
- **GPU**: Recommended but not required (CUDA-compatible for faster training)
- **Storage**: At least 10GB free space for model downloads

### Dependencies
All dependencies are automatically installed:
- PyTorch
- Transformers
- Flask & Flask-CORS
- Datasets
- Accelerate
- Pandas
- Hugging Face Hub
- pyngrok (for Colab/Kaggle)

## 🌐 Cloud Platforms

### Google Colab
Install and run in a Colab cell
!pip install tunestudio
import tunestudio
tunestudio.main.run_app_with_ngrok()

text

### Kaggle Notebooks
Install and run in a Kaggle cell
import subprocess
subprocess.run(["pip", "install", "tunestudio"])
import tunestudio
tunestudio.main.run_app_with_ngrok()

text

## 🚨 Authentication for Gated Models

Some models (like Llama) require Hugging Face authentication:

Login to Hugging Face
huggingface-cli login

text

Or set your token as an environment variable:
export HUGGINGFACE_HUB_TOKEN=your_token_here

text

## 🔍 Troubleshooting

### Common Issues

**1. Model Not Loading**
- Ensure you have sufficient RAM/VRAM
- For gated models, make sure you're authenticated with Hugging Face
- Try a smaller model first (e.g., `distilbert-base-uncased`)

**2. Dataset Loading Failed**
- Check file path is correct for local files
- Ensure CSV has a `text` column
- For Hub datasets, check the dataset name is valid

**3. CUDA Out of Memory**
- Reduce batch size (try 8 or 4)
- Use a smaller model
- Enable gradient checkpointing (automatically handled)

**4. Slow Training**
- Consider using a GPU if available
- Reduce the number of epochs
- Use a smaller model for testing

## 📊 Performance Tips

- **GPU Usage**: Training is significantly faster with a CUDA-compatible GPU
- **Batch Size**: Start with 16, reduce if you encounter memory issues
- **Model Size**: Begin with smaller models (2B-7B parameters) for faster iteration
- **Dataset Size**: Larger datasets require more time but generally produce better results

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** and add tests
4. **Submit a pull request**

### Development Setup
git clone https://github.com/yourusername/tunestudio.git
cd tunestudio
pip install -e .

text

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Transformers](https://huggingface.co/transformers/) by Hugging Face
- UI powered by [React](https://reactjs.org/) and [Tailwind CSS](https://tailwindcss.com/)
- Backend built with [Flask](https://flask.palletsprojects.com/)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ankitdutta428/tunestudio/issues)
- **Documentation**: [Wiki](https://github.com/ankitdutta428/tunestudio)
- **Email**: services.ai.minerva@gmail.com

---

**Made with ❤️ for the AI community**