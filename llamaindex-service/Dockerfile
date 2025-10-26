FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

RUN pip install \
    llama-index \
    llama-index-vector-stores-qdrant \
    qdrant-client \
    fastapi \
    uvicorn \
    python-multipart \
    openai

COPY app.py .
COPY wait-for-it.sh .
RUN chmod +x wait-for-it.sh

EXPOSE 8000

CMD [ "python", "app.py" ]