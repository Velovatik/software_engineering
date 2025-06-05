FROM python:3.9-slim

WORKDIR /app

# Install netcat and postgresql client libraries
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add current directory to PYTHONPATH
ENV PYTHONPATH=/app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 