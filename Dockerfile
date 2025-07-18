# Use official Node.js 18 image
FROM node:18-slim

# Create app directory
WORKDIR /app

# Copy the ai-accelerated directory
COPY ai-accelerated/ ./ai-accelerated/

# Change to ai-accelerated directory
WORKDIR /app/ai-accelerated

# Install dependencies
RUN npm ci --omit=dev

# Create logs directory
RUN mkdir -p logs

# Expose health port
EXPOSE 3000

# Deploy commands and start the bot
CMD ["sh", "-c", "npm run deploy && npm start"]
