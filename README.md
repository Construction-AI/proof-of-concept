# Distributed RAG Document Synthesis Platform

An asynchronous, containerized Retrieval-Augmented Generation (RAG) backend designed to automate the ingestion, chunking, and semantic synthesis of uploaded documents without blocking the main application thread.

![Logo](./wiki/infra_diagram.svg)

## Core Engineering Problem
Building a multi-tenant LLM application requires strict isolation of context (per-project data) and asynchronous processing to prevent API timeouts during heavy document ingestion. Furthermore, distributed backend services require robust observability to trace vector search latency and inference bottlenecks.

## System Architecture & Trade-offs

* **Vector Search Engine (Qdrant):** Handles high-dimensional similarity searches. Chosen over in-memory indexes to support production-grade latency and isolated, per-project vector collections.
* **Object Storage (MinIO):** Decouples raw file storage from the main database, allowing horizontal scaling of file blobs (PDFs, text) independent of relational metadata.
* **Data Orchestration (LlamaIndex):** Manages the ETL pipeline—parsing documents, applying chunking strategies, and generating embeddings prior to Qdrant insertion.
* **Observability Stack (Grafana & Loki):** Integrated telemetry for the backend microservices. Loki aggregates asynchronous worker logs, while Grafana visualizes system metrics (memory, API latency, inference times).
* **State Management (SQLite -> PostgreSQL):** Currently utilizing SQLite for MVP metadata storage. The schema and ORM are designed for a zero-friction migration to PostgreSQL to support concurrent write scaling.

## Data Flow
1. **Ingestion:** Client uploads documents to a specific Project Workspace -> FastAPI stores raw files in MinIO.
2. **Processing:** LlamaIndex extracts text, chunks data, and generates embeddings asynchronously.
3. **Storage:** Vectors are pushed to Qdrant (segregated by project ID); metadata is written to SQLite.
4. **Retrieval (Chat / Synthesis):** Client queries the assistant -> K-NN search on Qdrant filters by project -> LLM synthesizes a response or generates a new document based strictly on the localized context.

## Local Deployment
```bash
# Deploys the application, databases, and observability stack
docker-compose up --build -d
```