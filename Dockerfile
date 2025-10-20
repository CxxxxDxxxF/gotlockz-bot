# Use official Node.js 18 image
FROM node:25-slim

# Create app directory
WORKDIR /app

# Copy the entire project
COPY . .

# Change to ai-accelerated directory where the actual dependencies are
WORKDIR /app/ai-accelerated

# Debug: List files to see what was copied
RUN ls -la

# Install dependencies using npm install instead of npm ci
RUN npm install --omit=dev

# Create logs directory
RUN mkdir -p logs

# Expose health port
EXPOSE 3000

# Deploy commands and start the bot
CMD ["sh", "-c", "npm run deploy && npm start"] 