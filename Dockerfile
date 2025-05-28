FROM python:3.11-slim

# Install system deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      tesseract-ocr \
      libtesseract-dev \
      libsm6 \
      libxext6 \
      libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python deps (including GitHub MLB-StatsAPI)
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy your bot code
COPY . .

# Start the bot
CMD ["python", "bot.py"]
