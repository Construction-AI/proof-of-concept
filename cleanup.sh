#!/bin/bash
echo "Removing containers"
docker rm poc-frontend-1
docker rm poc-llamaindex-1
docker rm poc-ollama-1
docker rm poc-qdrant-1

echo ""
echo "Removing volumes"
docker volume rm poc_index_data
# docker volume rm poc_ollama
docker volume rm poc_uploaded_docs

