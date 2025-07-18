# Use official Node.js 18 image
FROM node:24-slim

# Create app directory
WORKDIR /app

# Copy the entire project
COPY . .

# Change to ai-accelerated directory where the actual dependencies are
WORKDIR /app/ai-accelerated

# Install dependencies
RUN npm ci --only=production

# Create logs directory
RUN mkdir -p logs

# Expose health port
EXPOSE 3000

# Deploy commands and start the bot
CMD ["sh", "-c", "npm run deploy && npm start"] 