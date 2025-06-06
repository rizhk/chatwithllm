
#!/bin/sh
mkdir -p ./llama.cpp/models

# Create necessary directories
mkdir -p ./llama.cpp/build/bin


MODEL_DIR="llama.cpp/models"
FILE_ID="1RPGR7DFcZMl4w5FstmNTI_BLZ0Fcm4Ji"  # Your GDrive File ID
MODEL_PATH="$MODEL_DIR/gpt2.gguf"

mkdir -p "$MODEL_DIR"

if [ ! -f "$MODEL_PATH" ]; then

    echo "Downloading GGUF model using gdown..."
    gdown "https://drive.google.com/uc?id=$FILE_ID" -O "$MODEL_PATH"
    
    echo "Model saved to $MODEL_PATH"
else
    echo "Model already exists. Skipping download."
fi

# Start llama.cpp server
# echo "Starting llama.cpp server with model at $MODEL_PATH..."
# python -m llama_cpp.server --model "$MODEL_PATH" --host 0.0.0.0 --port 8000
# echo "started llama.cpp server with model at $MODEL_PATH..."

# Wait for server to start
SERVER_PID=$!

echo "Waiting for llama server to start..."
for i in {1..10}; do
    curl -s http://localhost:8000/v1/models > /dev/null && {
        echo "Llama Server is up!"
        break
    }
    sleep 1
done

# Start FastAPI app
uvicorn main:app --host 0.0.0.0 --port 10000 --reload