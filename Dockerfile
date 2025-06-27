# Use official Node.js 18 image
FROM node:18-slim

# Create app directory
WORKDIR /app

# Copy package manifests & install deps
COPY package*.json ./
RUN npm ci

# Copy rest of the source
COPY . .

# Build TypeScript
RUN npm run build

# Expose health port
EXPOSE 3000

# Start the bot
CMD ["node", "dist/index.js"]
