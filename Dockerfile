<<<<<<< HEAD
# Dockerfile

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run the bot
CMD ["python", "main.py"]
=======
FROM python:3.11-slim

# 1) Install system packages: git (so pip can fetch GitHub repos) and tesseract-ocr (for pytesseract)
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
         git \
         tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# 2) Now that git exists, pip can install the "git+https://..." dependency successfully
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# 3) Finally, start your bot
CMD ["python", "main.py", "--log-level", "INFO"]
>>>>>>> cceffda894c274128b92ea45ab52674f56d45a11
