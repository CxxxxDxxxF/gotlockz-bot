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
