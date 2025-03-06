#!/bin/bash
# Start Ollama in the background.
/bin/ollama serve &
# Record Process ID.
pid=$!
# Pause for Ollama to start.
sleep 5

# Function to check if model exists
model_exists() {
    ollama list | grep -q "$1"
    return $?
}

# Pull Qwen2.5 if it doesn't exist
if model_exists "qwen2.5:14b"; then
    echo "🟢 QWEN2.5:14B model already exists"
else
    echo "🔴 Retrieving QWEN2.5:14B model..."
    ollama pull qwen2.5:14b
    echo "🟢 QWEN2.5:14B model pulled successfully"
fi

# Pull nomic-embed-text if it doesn't exist
if model_exists "nomic-embed-text"; then
    echo "🟢 NOMIC-EMBED-TEXT model already exists"
else
    echo "🔴 Retrieving NOMIC-EMBED-TEXT model..."
    ollama pull nomic-embed-text
    echo "🟢 NOMIC-EMBED-TEXT model pulled successfully"
fi

echo "🟢 All models ready!"

# Wait for Ollama process to finish.
wait $pid