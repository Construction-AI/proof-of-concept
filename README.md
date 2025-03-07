# Document Processing and RAG System

## Overview

This project implements a document processing and retrieval system using Retrieval-Augmented Generation (RAG). It allows users to upload documents, analyze them, and generate content based on the document information using LLMs.

## Architecture

The system consists of several microservices working together:

- **Frontend UI**: A Streamlit-based web interface for user interaction
- **LlamaIndex Service**: Handles document processing, indexing, and RAG queries
- **Qdrant**: Vector database for storing document embeddings
- **Ollama**: Local LLM service for text generation and embeddings

## Features

- Document upload and management
- Automatic document indexing and vectorization
- Document-based content generation using RAG
- Query interface for document information retrieval

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Internet connection for downloading initial models

### Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:Construction-AI/proof-of-concept.git
   cd proof-of-concept
   ```

2. Configure environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
	QUERY_MODEL=qwen2.5:14b
	EMBEDDINGS_MODEL=nomic-embed-text
	OLLAMA_BASE_URL=http://ollama:11434
	QDRANT_URL=http://qdrant:6333
	LLAMAINDEX_HOST=0.0.0.0
	LLAMAINDEX_PORT=8000
	LLAMAINDEX_BASE_URL=http://llamaindex:8000
	OLLAMA_TIMEOUT=99999
   ```

1. Start the services:
   ```bash
   docker-compose up -d
   ```

2. Wait for all services to initialize. This might take a few minutes on first run as the LLM models are downloaded.

## Usage

Access the application at: http://localhost:8501

### Document Management

1. Navigate to the "Manage Files" tab
2. Upload documents using the file uploader
3. View and manage your uploaded documents

### Document Processing

1. Go to the "Generate Document" tab
2. Fill in the project details
3. Select the document type to generate
4. Click "Generate" to create content based on your uploaded documents

## Services

- **Frontend UI**: http://localhost:8501
- **LlamaIndex API**: http://localhost:8000
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Ollama**: http://localhost:11434 (API only)

## Data Persistence

The system uses Docker volumes to persist data:
- `uploaded_docs`: Stores all uploaded documents
- `index_data`: Stores document indices and vector embeddings
- `ollama`: Stores downloaded LLM models

## Troubleshooting

- If services fail to start, check Docker logs:
  ```bash
  docker-compose logs [service-name]
  ```

- For model issues, ensure you have sufficient disk space for the LLM models

- If the UI is unresponsive, check if all backend services are running:
  ```bash
  docker-compose ps
  ```