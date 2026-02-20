FROM python:3.11-bookworm

WORKDIR /app

# Copy and install shared library
COPY shared_schema/ /shared_schema/
RUN pip install /shared_schema/

COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/ .