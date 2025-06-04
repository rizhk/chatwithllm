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

# Start llama.cpp model server
chmod +x ./llama.cpp/build/bin/llama-cli
./llama.cpp/build/bin/llama-cli -m ./llama.cpp/models/tinyllama.gguf -cnv -b 512 --port 8000 &

# Start LiteLLM proxy
litellm --port 4000 --model llama-cpp=custom_openai/api_base=http://localhost:8000 &

# Start FastAPI app
uvicorn main:app --host 0.0.0.0 --port 10000 --reload