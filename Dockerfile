# Use official Node.js 18 image
FROM node:18-slim

# Install system dependencies for sharp
RUN apt-get update && apt-get install -y \
    libvips \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy package files first for better caching
COPY ai-accelerated/package*.json ./ai-accelerated/

# Change to ai-accelerated directory
WORKDIR /app/ai-accelerated

# Install dependencies with cache mount for faster builds
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev --prefer-offline --no-audit && \
    npm rebuild sharp --platform=linux --arch=x64

# Copy source code (after dependencies for better caching)
COPY ai-accelerated/src/ ./src/
COPY ai-accelerated/deploy-commands.js ./
COPY ai-accelerated/deploy.sh ./
COPY ai-accelerated/env.example ./

# Create logs directory
RUN mkdir -p logs

# Expose health port
EXPOSE 3000

# Deploy commands and start the bot
CMD ["sh", "-c", "npm run deploy && npm start"]
