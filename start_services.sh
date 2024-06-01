#!/bin/sh

# Start the Ollama service in the background
ollama serve &

# Pull the required model
ollama run llama3

python3 loader.py

# Run the Python application
python3 main.py
