FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting GotLockz Bot and Dashboard..."\n\
python3 dashboard/app.py &\n\
sleep 3\n\
python3 main.py\n\
wait' > /app/start.sh && chmod +x /app/start.sh

# Expose dashboard port
EXPOSE 8080

# Set environment variables
ENV DASHBOARD_URL=http://localhost:8080

# Start both services
CMD ["/app/start.sh"]
