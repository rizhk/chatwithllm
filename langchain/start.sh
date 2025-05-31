# mkdir -p ~/mamba-postgres/data
# initdb -D ~/mamba-postgres/data
micromamba activate torch_env
pg_ctl -D ~/mamba-postgres/data -l ~/mamba-postgres/logfile start
ollama run --model gemma:2b --port 11434 --host

# litellm --model ollama/gemma:2b --api_base http://127.0.0.1:11434 --host 127.0.0.1
sudo litellm --config config.yaml --debug # somehow this works with sudo only