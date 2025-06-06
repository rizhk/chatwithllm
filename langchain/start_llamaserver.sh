#!/bin/sh

MODEL_DIR="llama.cpp/models"
MODEL_PATH="$MODEL_DIR/gpt2.gguf"


# # Start FastAPI
# APP_PORT=${PORT:-10000}
# echo "Starting FastAPI on port $APP_PORT..."
# uvicorn main:app --host 0.0.0.0 --port $APP_PORT --reload &

# Download model if needed...
# ... (same as before)

# Start LLM server in background
echo "Starting LLM server..."
python -m llama_cpp.server --model "$MODEL_PATH" --host 0.0.0.0 --port 8000 > ./llm_server.log 2>&1 &
LLM_PID=$!
echo "Started LLM server with PID $LLM_PID"

# Wait for server to become available
echo "Waiting for LLM server to respond..."
for i in {1..30}; do
    curl -s http://localhost:8000/v1/models > /dev/null && {
        echo "LLM server is up!"
        break
    }
    echo "Retrying LLM server connection ($i/30)..."
    sleep 2
done

# Check if server is still running
if ! kill -0 $LLM_PID 2>/dev/null; then
    echo "LLM server failed to start. Check ./llm_server.log"
    cat ./llm_server.log
    exit 1
fi

