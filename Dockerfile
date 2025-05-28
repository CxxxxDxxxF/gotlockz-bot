# Use the official slim Python image so we can apt‑get
FROM python:3.11-slim

# Install Tesseract OCR system package
RUN apt-get update \
 && apt-get install -y --no-install-recommends tesseract-ocr libtesseract-dev \
 && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# before installing requirements…
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy the rest of your bot code
COPY . .

# Expose no ports (Discord bot only)
CMD ["python", "bot.py"]
