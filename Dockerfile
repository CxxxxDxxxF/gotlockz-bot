# Use official Node.js 18 image
FROM node:18-slim

# Create app directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
COPY ai-accelerated/package*.json ./ai-accelerated/

# Install workspace dependencies
RUN npm ci

# Copy the rest of the files
COPY . .

# Change to ai-accelerated directory
WORKDIR /app/ai-accelerated

# Create logs directory
RUN mkdir -p logs

# Expose health port
EXPOSE 3000

# Deploy commands and start the bot
CMD ["sh", "-c", "npm run deploy && npm start"] 