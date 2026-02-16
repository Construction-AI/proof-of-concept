#!/bin/bash
# Start Ollama in the background.

set -e

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

# Pull query model if it doesn't exist
if model_exists "$OLLAMA_MODEL"; then
    echo "🟢 $OLLAMA_MODEL model already exists"
else
    echo "🔴 Retrieving $OLLAMA_MODEL model..."
    ollama pull $OLLAMA_MODEL
    echo "🟢 $OLLAMA_MODEL model pulled successfully"
fi

# Pull embeddings model if it doesn't exist
if model_exists "$OLLAMA_EMBEDDING_MODEL"; then
    echo "🟢 $OLLAMA_EMBEDDING_MODEL model already exists"
else
    echo "🔴 Retrieving $OLLAMA_EMBEDDING_MODEL model..."
    ollama pull $OLLAMA_EMBEDDING_MODEL
    echo "🟢 $OLLAMA_EMBEDDING_MODEL model pulled successfully"
fi

echo "🟢 All models ready!"

# Wait for Ollama process to finish.
wait $pid