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

# Pull query model if it doesn't exist
if model_exists "$QUERY_MODEL"; then
    echo "🟢 $QUERY_MODEL model already exists"
else
    echo "🔴 Retrieving $QUERY_MODEL model..."
    ollama pull $QUERY_MODEL
    echo "🟢 $QUERY_MODEL model pulled successfully"
fi

# Pull $EMBEDDINGS_MODEL if it doesn't exist
if model_exists "$EMBEDDINGS_MODEL"; then
    echo "🟢 $EMBEDDINGS_MODEL model already exists"
else
    echo "🔴 Retrieving $EMBEDDINGS_MODEL model..."
    ollama pull $EMBEDDINGS_MODEL
    echo "🟢 $EMBEDDINGS_MODEL model pulled successfully"
fi

echo "🟢 All models ready!"

# Wait for Ollama process to finish.
wait $pid