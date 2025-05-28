FROM python:3.11-slim

# 1) system deps…
RUN apt-get update && apt-get install -y --no-install-recommends \
      tesseract-ocr libtesseract-dev libsm6 libxext6 libglib2.0-0 unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) copy & install PyPI deps
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 3) vendor MLB-StatsAPI
COPY MLB-StatsAPI-master.zip .
RUN unzip MLB-StatsAPI-master.zip \
 && pip install ./MLB-StatsAPI-master

# 4) copy your code
COPY . .

CMD ["python", "bot.py"]
