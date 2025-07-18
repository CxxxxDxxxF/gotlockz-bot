# Use official Node.js 18 image
FROM node:18-slim

# Create app directory
WORKDIR /app

# Copy package files first for better caching
COPY ai-accelerated/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy the rest of the ai-accelerated directory
COPY ai-accelerated/ ./

# Create logs directory
RUN mkdir -p logs

# Expose health port
EXPOSE 3000

# Deploy commands and start the bot
CMD ["sh", "-c", "npm run deploy && npm start"] 