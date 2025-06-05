# mkdir -p ~/mamba-postgres/data
# initdb -D ~/mamba-postgres/data
# micromamba activate torch_env
# fastapi dev main.py
# pg_ctl -D ~/mamba-postgres/data -l ~/mamba-postgres/logfile start
# ollama run --model gemma:2b --port 11434 --host

# # litellm --model ollama/gemma:2b --api_base http://127.0.0.1:11434 --host 127.0.0.1
# sudo litellm --config config.yaml --debug # somehow this works with sudo only

#!/bin/sh

# Start llama.cpp model server
#!/bin/sh
mkdir -p ./llama.cpp/models

# Create necessary directories
mkdir -p ./llama.cpp/build/bin

#!/bin/bash


MODEL_DIR="llama.cpp/models"
FILE_ID="1RPGR7DFcZMl4w5FstmNTI_BLZ0Fcm4Ji"  # Your GDrive File ID
MODEL_PATH="$MODEL_DIR/gpt2.gguf"

mkdir -p "$MODEL_DIR"

if [ ! -f "$MODEL_PATH" ]; then
    echo "Installing gdown..."
    pip install gdown

    echo "Downloading GGUF model using gdown..."
    gdown "https://drive.google.com/uc?id=$FILE_ID" -O "$MODEL_PATH"
    
    echo "Model saved to $MODEL_PATH"
else
    echo "Model already exists. Skipping download."
fi

# Start llama.cpp server 
python -m llama_cpp.server --model "$MODEL_PATH" --host 0.0.0.0 --port 8000

# curl -L https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf  -o ./llama.cpp/models/tinyllama.gguf

# Start llama.cpp model server
# python -m llama_cpp.server --model ./llama.cpp/models/gpt2.gguf --host 0.0.0.0 --port 8000

# Start LiteLLM proxy
# litellm --port 4000 --model custom_openai/llama-cpp --api_base http://localhost:8000 &

# Start FastAPI app
uvicorn main:app --host 0.0.0.0 --port 10000 --reload