# Production Dockerfile for GotLockz Discord Bot
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install minimal system dependencies (no OCR dependencies needed)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy bot source code
COPY src/ ./src/
COPY main.py .

# Create data directory
RUN mkdir -p data

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash bot && \
    chown -R bot:bot /app
USER bot

# Set Python path
ENV PYTHONPATH=/app

# Run the bot
CMD ["python", "main.py"]
