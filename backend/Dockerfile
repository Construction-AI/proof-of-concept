FROM python:3.11-bookworm

WORKDIR /app

RUN mkdir -p /static
RUN mkdir -p /data

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy and install shared library
COPY shared_schema/ /shared_schema/
RUN pip install /shared_schema/

# Copy and install requirements
COPY backend/requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

COPY backend/ .

# EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
