FROM ollama/ollama

ARG MODEL=qwen2.5-coder:7b

# Start the server, pull the model, then stop the server
RUN ollama serve & sleep 5 && ollama pull ${MODEL} && kill $(pidof ollama)
