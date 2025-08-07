from setuptools import setup, find_packages
import os

# Read the README file for the long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

setup(
    name="tunestudio",  
    version="0.0.11",
    author="Minerva AI",
    author_email="services.ai.minerva@gmail.com",
    description="An all in one platform for finetuning your LLM models using your Google Colab, Kaggle or Local resources.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ankitdutta428/tunestudio",  
    packages=find_packages(),
    include_package_data=True,  # CRUCIAL: Includes non-Python files
    install_requires=[
        "flask>=2.0.0",
        "flask-cors>=4.0.0",
        "pandas>=1.3.0",
        "transformers>=4.20.0",
        "torch>=1.12.0",
        "pyngrok>=6.0.0",
        "huggingface-hub>=0.10.0",
        "datasets>=2.0.0",
        "accelerate>=0.20.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "tunestudio=tunestudio.main:run_app",
            "tunestudio-colab=tunestudio.main:run_app_with_ngrok",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    keywords="machine-learning, llm, fine-tuning, transformers, no-code, ui, tunestudio",
)
