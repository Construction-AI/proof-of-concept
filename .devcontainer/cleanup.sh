#!/bin/bash
echo "Stopping all Docker containers..."
docker stop $(docker ps -q) || true

echo "Removing all containers..."
docker rm $(docker ps -aq) || true

echo "Removing volumes..."
docker volume rm poc_qdrant_data poc_uploaded_docs poc_index_data poc_ollama || true

echo "Pruning networks..."
docker network prune -f

echo "Pruning system..."
docker system prune -f

echo "Cleanup complete!"